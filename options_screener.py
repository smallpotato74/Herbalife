#!/usr/bin/env python3
"""
options_screener.py
====================
用 ATR + IV/HV regime + Greeks(Delta/Gamma/Theta/Vega) 篩選高質期權嘅 screener。

特點
----
- 資料來源可換：YFinanceProvider(免費,真實) / TradierProvider(需 API key) / SampleProvider(離線 demo)
- 自己用 Black-Scholes 計 Greeks（唔靠數據商），用合約自身 IV
- IV regime 用 IV/HV ratio + HV Rank 做可計算嘅 proxy（真 IVR 需要 IV 歷史,見下面註)
- 用 ATR 計 expected move,決定 strike 距離合唔合理
- 綜合評分排序,輸出每隻標的最高分嘅 call/put 候選

用法
----
# 真實數據(你部機要有網):
python options_screener.py --tickers AAPL MSFT NVDA --side auto

# 離線 demo(無網都跑到,用合成數據):
python options_screener.py --demo --tickers AAPL NVDA KO

# 指定方向 + 風險偏好:
python options_screener.py --tickers SPY --side sell --min-dte 30 --max-dte 45

⚠️ 教育用途,非投資建議。
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional

# ----------------------------------------------------------------------------
# 1) 基礎數學:Black-Scholes Greeks
# ----------------------------------------------------------------------------

SQRT_2PI = math.sqrt(2.0 * math.pi)


def _norm_cdf(x: float) -> float:
    """標準常態 CDF,用 erf,免裝 scipy。"""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / SQRT_2PI


@dataclass
class Greeks:
    delta: float
    gamma: float
    theta_per_day: float   # 每日 time decay (期權價單位)
    vega_per_1pct: float   # IV 升 1% 期權升幾多


def bs_greeks(S: float, K: float, dte_days: float, iv: float,
              r: float = 0.045, is_call: bool = True,
              q: float = 0.0) -> Greeks:
    """
    S: 現價, K: 行使價, dte_days: 距到期日數, iv: 引伸波幅(小數,如0.30),
    r: 無風險利率, q: 股息率。
    回傳 delta/gamma/theta(每日)/vega(每1%)。
    """
    T = max(dte_days, 1e-6) / 365.0
    if iv <= 0 or S <= 0 or K <= 0:
        return Greeks(0.0, 0.0, 0.0, 0.0)

    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * iv * iv) * T) / (iv * sqrtT)
    d2 = d1 - iv * sqrtT
    pdf_d1 = _norm_pdf(d1)
    disc_q = math.exp(-q * T)
    disc_r = math.exp(-r * T)

    if is_call:
        delta = disc_q * _norm_cdf(d1)
        theta_year = (
            -(S * disc_q * pdf_d1 * iv) / (2 * sqrtT)
            - r * K * disc_r * _norm_cdf(d2)
            + q * S * disc_q * _norm_cdf(d1)
        )
    else:
        delta = -disc_q * _norm_cdf(-d1)
        theta_year = (
            -(S * disc_q * pdf_d1 * iv) / (2 * sqrtT)
            + r * K * disc_r * _norm_cdf(-d2)
            - q * S * disc_q * _norm_cdf(-d1)
        )

    gamma = disc_q * pdf_d1 / (S * iv * sqrtT)
    vega = S * disc_q * pdf_d1 * sqrtT  # per 1.0 vol

    return Greeks(
        delta=delta,
        gamma=gamma,
        theta_per_day=theta_year / 365.0,
        vega_per_1pct=vega / 100.0,
    )


# ----------------------------------------------------------------------------
# 2) ATR / HV (歷史波幅) 計算
# ----------------------------------------------------------------------------

def atr_wilder(highs, lows, closes, period: int = 14) -> float:
    """Wilder smoothing ATR(股價單位)。highs/lows/closes 同長度。"""
    n = len(closes)
    if n < period + 1:
        return float("nan")
    trs = []
    for i in range(1, n):
        h, l, pc = highs[i], lows[i], closes[i - 1]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    a = sum(trs[:period]) / period
    for t in trs[period:]:
        a = (a * (period - 1) + t) / period
    return a


def hist_vol(closes, window: int = 20, annualize: int = 252) -> float:
    """年化歷史波幅(realized vol),用日對數收益率。"""
    if len(closes) < window + 1:
        return float("nan")
    rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    sample = rets[-window:]
    mean = sum(sample) / len(sample)
    var = sum((x - mean) ** 2 for x in sample) / (len(sample) - 1)
    return math.sqrt(var) * math.sqrt(annualize)


def hv_rank(closes, window: int = 20, lookback: int = 252) -> float:
    """
    HV Rank(%):當前 HV 喺過去 lookback 日嘅 rolling HV 區間嘅位置。
    用嚟做 IVR 唔可得時嘅 regime proxy。
    """
    if len(closes) < window + lookback + 1:
        return float("nan")
    rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    rolling = []
    for end in range(window, len(rets) + 1):
        seg = rets[end - window:end]
        m = sum(seg) / len(seg)
        v = sum((x - m) ** 2 for x in seg) / (len(seg) - 1)
        rolling.append(math.sqrt(v) * math.sqrt(252))
    rolling = rolling[-lookback:]
    cur = rolling[-1]
    lo, hi = min(rolling), max(rolling)
    if hi - lo < 1e-9:
        return 50.0
    return (cur - lo) / (hi - lo) * 100.0


# ----------------------------------------------------------------------------
# 3) 資料模型
# ----------------------------------------------------------------------------

@dataclass
class Underlying:
    ticker: str
    spot: float
    atr: float
    hv20: float
    hv_rank: float
    atm_iv: float                      # 由 chain 取近 ATM 嘅 IV
    next_earnings: Optional[date] = None


@dataclass
class OptionContract:
    ticker: str
    expiry: date
    dte: int
    strike: float
    is_call: bool
    bid: float
    ask: float
    last: float
    volume: int
    open_interest: int
    iv: float
    greeks: Greeks = field(default=None)

    @property
    def mid(self) -> float:
        if self.bid > 0 and self.ask > 0:
            return (self.bid + self.ask) / 2
        return self.last

    @property
    def spread_pct(self) -> float:
        m = self.mid
        if m <= 0 or self.ask <= 0:
            return 1.0
        return (self.ask - self.bid) / m


# ----------------------------------------------------------------------------
# 4) 資料來源(Provider)
# ----------------------------------------------------------------------------

class DataProvider:
    def get_underlying(self, ticker: str) -> Underlying: ...
    def get_chain(self, ticker: str, u: Underlying,
                  min_dte: int, max_dte: int) -> list[OptionContract]: ...


class YFinanceProvider(DataProvider):
    """免費真實數據。需要:pip install yfinance,同你部機要有網。"""

    def __init__(self, r: float = 0.045):
        import yfinance as yf  # 延遲 import
        self.yf = yf
        self.r = r

    def get_underlying(self, ticker: str) -> Underlying:
        t = self.yf.Ticker(ticker)
        hist = t.history(period="2y", auto_adjust=False)
        if hist.empty:
            raise RuntimeError(f"{ticker}: 攞唔到股價(可能無網或代號錯)")
        closes = hist["Close"].tolist()
        highs = hist["High"].tolist()
        lows = hist["Low"].tolist()
        spot = closes[-1]
        atr = atr_wilder(highs, lows, closes, 14)
        hv20 = hist_vol(closes, 20)
        hvr = hv_rank(closes, 20, 252)

        # earnings 日期(best effort)
        nx = None
        try:
            cal = t.get_earnings_dates(limit=8)
            if cal is not None and not cal.empty:
                future = [d.date() for d in cal.index if d.date() >= date.today()]
                nx = min(future) if future else None
        except Exception:
            pass

        # ATM IV 暫時留空,等 get_chain 填
        return Underlying(ticker, spot, atr, hv20, hvr, atm_iv=float("nan"),
                          next_earnings=nx)

    def get_chain(self, ticker, u, min_dte, max_dte):
        t = self.yf.Ticker(ticker)
        out: list[OptionContract] = []
        today = date.today()
        atm_ivs = []
        for exp_str in t.options:
            exp = datetime.strptime(exp_str, "%Y-%m-%d").date()
            dte = (exp - today).days
            if dte < min_dte or dte > max_dte:
                continue
            oc = t.option_chain(exp_str)
            for df, is_call in ((oc.calls, True), (oc.puts, False)):
                for _, row in df.iterrows():
                    iv = float(row.get("impliedVolatility", 0) or 0)
                    if iv <= 0:
                        continue
                    c = OptionContract(
                        ticker=ticker, expiry=exp, dte=dte,
                        strike=float(row["strike"]), is_call=is_call,
                        bid=float(row.get("bid", 0) or 0),
                        ask=float(row.get("ask", 0) or 0),
                        last=float(row.get("lastPrice", 0) or 0),
                        volume=int(row.get("volume", 0) or 0),
                        open_interest=int(row.get("openInterest", 0) or 0),
                        iv=iv,
                    )
                    c.greeks = bs_greeks(u.spot, c.strike, dte, iv,
                                         r=self.r, is_call=is_call)
                    out.append(c)
                    if abs(c.strike - u.spot) / u.spot < 0.03:
                        atm_ivs.append(iv)
        if atm_ivs:
            u.atm_iv = sum(atm_ivs) / len(atm_ivs)
        return out


class TradierProvider(DataProvider):
    """
    Tradier brokerage API(有真 Greeks + IV)。
    需要 token: https://documentation.tradier.com/
    用法: TradierProvider(token="...", sandbox=True)
    """

    def __init__(self, token: str, sandbox: bool = True, r: float = 0.045):
        import requests
        self.requests = requests
        self.token = token
        self.base = ("https://sandbox.tradier.com/v1" if sandbox
                     else "https://api.tradier.com/v1")
        self.r = r
        self.h = {"Authorization": f"Bearer {token}",
                  "Accept": "application/json"}

    def _get(self, path, params):
        resp = self.requests.get(self.base + path, params=params,
                                 headers=self.h, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_underlying(self, ticker):
        # 日線歷史
        hist = self._get("/markets/history",
                         {"symbol": ticker, "interval": "daily"})
        days = hist.get("history", {}).get("day", [])
        closes = [d["close"] for d in days]
        highs = [d["high"] for d in days]
        lows = [d["low"] for d in days]
        spot = closes[-1]
        return Underlying(ticker, spot,
                          atr_wilder(highs, lows, closes, 14),
                          hist_vol(closes, 20),
                          hv_rank(closes, 20, 252),
                          atm_iv=float("nan"))

    def get_chain(self, ticker, u, min_dte, max_dte):
        exps = self._get("/markets/options/expirations",
                         {"symbol": ticker}).get("expirations", {}).get("date", [])
        if isinstance(exps, str):
            exps = [exps]
        today = date.today()
        out, atm_ivs = [], []
        for exp_str in exps:
            exp = datetime.strptime(exp_str, "%Y-%m-%d").date()
            dte = (exp - today).days
            if dte < min_dte or dte > max_dte:
                continue
            data = self._get("/markets/options/chains",
                             {"symbol": ticker, "expiration": exp_str,
                              "greeks": "true"})
            opts = data.get("options", {}).get("option", []) or []
            for o in opts:
                g = o.get("greeks") or {}
                iv = float(g.get("mid_iv") or g.get("smv_vol") or 0)
                if iv <= 0:
                    continue
                is_call = o["option_type"] == "call"
                c = OptionContract(
                    ticker, exp, dte, float(o["strike"]), is_call,
                    float(o.get("bid") or 0), float(o.get("ask") or 0),
                    float(o.get("last") or 0), int(o.get("volume") or 0),
                    int(o.get("open_interest") or 0), iv,
                )
                # Tradier 自帶 Greeks,但統一用自己 BS 保持一致
                c.greeks = bs_greeks(u.spot, c.strike, dte, iv,
                                     r=self.r, is_call=is_call)
                out.append(c)
                if abs(c.strike - u.spot) / u.spot < 0.03:
                    atm_ivs.append(iv)
        if atm_ivs:
            u.atm_iv = sum(atm_ivs) / len(atm_ivs)
        return out


# ----------------------------------------------------------------------------
# 5) 篩選 + 評分
# ----------------------------------------------------------------------------

@dataclass
class ScreenConfig:
    side: str = "auto"          # auto / buy / sell
    min_dte: int = 30
    max_dte: int = 60
    min_oi: int = 500
    min_vol: int = 50
    max_spread_pct: float = 0.06
    # 目標 delta 區間(絕對值)
    buy_delta: tuple = (0.55, 0.70)
    sell_delta: tuple = (0.15, 0.30)
    r: float = 0.045
    top_n: int = 5


def decide_side(u: Underlying, cfg: ScreenConfig) -> str:
    """
    用 IV/HV ratio 同 HV Rank 決定買/賣方向。
    IV/HV > 1.2 或 HV Rank 高 → 期權偏貴 → SELL
    IV/HV < 1.0 或 HV Rank 低 → 期權偏平 → BUY
    """
    if cfg.side in ("buy", "sell"):
        return cfg.side
    score = 0
    if not math.isnan(u.atm_iv) and not math.isnan(u.hv20) and u.hv20 > 0:
        ratio = u.atm_iv / u.hv20
        if ratio > 1.2:
            score += 1
        elif ratio < 1.0:
            score -= 1
    if not math.isnan(u.hv_rank):
        if u.hv_rank > 60:
            score += 1
        elif u.hv_rank < 30:
            score -= 1
    return "sell" if score > 0 else "buy" if score < 0 else "buy"


def expected_move_iv(spot: float, iv: float, dte: int) -> float:
    """市場引伸嘅 1 個標準差移動(股價單位):S × IV × √(DTE/365)。"""
    return spot * iv * math.sqrt(max(dte, 1) / 365.0)


def expected_move_atr(atr: float, dte: int) -> float:
    """
    用 ATR scale 嘅realized移動,但 ATR≈日內range≈1.4×日收市σ,
    要除返 1.4 先近似一個標準差,否則會高估。
    """
    return (atr / 1.4) * math.sqrt(max(dte, 1))


@dataclass
class Scored:
    contract: OptionContract
    side: str
    score: float
    expected_move: float
    reasons: list[str] = field(default_factory=list)


def score_contract(c: OptionContract, u: Underlying, side: str,
                   cfg: ScreenConfig) -> Optional[Scored]:
    # --- 硬性流動性過濾 ---
    if c.open_interest < cfg.min_oi:
        return None
    if c.volume < cfg.min_vol:
        return None
    if c.spread_pct > cfg.max_spread_pct:
        return None
    if c.greeks is None or c.mid <= 0:
        return None

    # 主要用市場引伸 1SD;ATR-based 做對照
    iv_ref = u.atm_iv if not math.isnan(u.atm_iv) else c.iv
    em = expected_move_iv(u.spot, iv_ref, c.dte)
    em_atr = expected_move_atr(u.atr, c.dte)
    absdelta = abs(c.greeks.delta)
    reasons = []
    score = 0.0

    # --- 流動性分 (0~25) ---
    liq = min(25, (c.open_interest / 2000) * 12 + (c.volume / 500) * 8
              + (1 - min(c.spread_pct / cfg.max_spread_pct, 1)) * 5)
    score += liq
    reasons.append(f"流動性 {liq:.0f}/25 (OI={c.open_interest},spr={c.spread_pct*100:.1f}%)")

    # --- Delta 配合目標區間 (0~25) ---
    lo, hi = cfg.buy_delta if side == "buy" else cfg.sell_delta
    if lo <= absdelta <= hi:
        d_score = 25
    else:
        dist = min(abs(absdelta - lo), abs(absdelta - hi))
        d_score = max(0, 25 - dist * 100)
    score += d_score
    reasons.append(f"Delta {absdelta:.2f} → {d_score:.0f}/25 (目標{lo}-{hi})")

    # --- 到價空間配合 (0~25):比較 strike 距離 vs 1SD 預期移動 ---
    dist_to_strike = abs(c.strike - u.spot)
    if em <= 0:
        em_score = 0
    elif side == "buy":
        # 買方:strike 喺 1SD 之內最好(到價機會高),超過就遞減
        if dist_to_strike <= em:
            em_score = 25
        else:
            em_score = max(0, 25 - (dist_to_strike - em) / em * 25)
    else:
        # 賣方:short strike 至少 1SD 之外先安全;< 0.5SD 太近高分扣
        if dist_to_strike >= em:
            em_score = 25
        elif dist_to_strike >= 0.5 * em:
            em_score = 12 + (dist_to_strike - 0.5 * em) / (0.5 * em) * 13
        else:
            em_score = max(0, dist_to_strike / (0.5 * em) * 12)
    score += em_score
    reasons.append(f"到價配合 {em_score:.0f}/25 (距strike={dist_to_strike:.2f}, "
                   f"1SD(IV)={em:.2f}, ATR移動={em_atr:.2f})")

    # --- IV regime 分 (0~25) ---
    regime = 0
    if not math.isnan(u.atm_iv) and not math.isnan(u.hv20) and u.hv20 > 0:
        ratio = u.atm_iv / u.hv20
        if side == "sell":
            regime = max(0, min(25, (ratio - 1.0) / 0.5 * 25))
        else:  # buy 想 IV 平
            regime = max(0, min(25, (1.2 - ratio) / 0.5 * 25))
    score += regime
    reasons.append(f"IV regime {regime:.0f}/25 (IV/HV={u.atm_iv/u.hv20:.2f})"
                   if u.hv20 else f"IV regime {regime:.0f}/25")

    # --- earnings 警告(buy 前裸買扣分,IV crush 風險) ---
    if u.next_earnings and side == "buy":
        days_to_er = (u.next_earnings - date.today()).days
        if 0 <= days_to_er <= c.dte:
            score -= 8
            reasons.append(f"⚠️ 到期前有earnings({u.next_earnings}),IV crush風險 -8")

    return Scored(c, side, score, em, reasons)


def screen_ticker(provider: DataProvider, ticker: str,
                  cfg: ScreenConfig) -> tuple[Underlying, list[Scored]]:
    u = provider.get_underlying(ticker)
    chain = provider.get_chain(ticker, u, cfg.min_dte, cfg.max_dte)
    side = decide_side(u, cfg)
    scored = []
    for c in chain:
        # buy:同時考慮 call & put(由你方向睇法決定,呢度兩邊都評,等你揀)
        s = score_contract(c, u, side, cfg)
        if s:
            scored.append(s)
    scored.sort(key=lambda x: x.score, reverse=True)
    return u, scored[:cfg.top_n]


# ----------------------------------------------------------------------------
# 6) 離線 Demo Provider(合成數據,無網都跑到)
# ----------------------------------------------------------------------------

class SampleProvider(DataProvider):
    """
    用 seeded 隨機遊走生成 OHLC + 一條有 IV smile 嘅期權鏈。
    純為咗離線示範 screener 真係行得到,數據唔代表真實市場。
    """

    PRESETS = {
        # ticker: (起始價, 年化漂移, 年化波幅, atm_iv, 有冇earnings天數)
        "AAPL": (195.0, 0.12, 0.24, 0.22, 18),
        "NVDA": (120.0, 0.35, 0.52, 0.72, 9),
        "KO":   (62.0, 0.04, 0.14, 0.16, None),
        "SPY":  (540.0, 0.08, 0.13, 0.12, None),
    }

    def __init__(self, r: float = 0.045, seed: int = 42):
        self.r = r
        self.seed = seed

    def _gen_ohlc(self, S0, mu, sigma, n=520, seed=0):
        import random
        rng = random.Random(self.seed + seed)
        dt = 1 / 252
        closes = []
        s = S0
        for _ in range(n):
            z = rng.gauss(0, 1)
            s = s * math.exp((mu - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * z)
            closes.append(s)
        # 錨定:令最後收市 ≈ S0(demo 用,睇落貼近預設價)
        scale = S0 / closes[-1]
        closes = [c * scale for c in closes]
        highs, lows = [], []
        for c in closes:
            intraday = sigma * math.sqrt(dt) * c
            highs.append(c + abs(rng.gauss(0, 1)) * intraday * 0.7)
            lows.append(max(0.01, c - abs(rng.gauss(0, 1)) * intraday * 0.7))
        return highs, lows, closes

    def get_underlying(self, ticker):
        p = self.PRESETS.get(ticker.upper())
        if not p:
            raise RuntimeError(f"Demo 只有 {list(self.PRESETS)}")
        S0, mu, sigma, atm_iv, er_days = p
        stable = sum(ord(ch) for ch in ticker.upper())  # 穩定,唔受PYTHONHASHSEED影響
        highs, lows, closes = self._gen_ohlc(S0, mu, sigma, seed=stable)
        spot = closes[-1]
        nx = None
        if er_days is not None:
            from datetime import timedelta
            nx = date.today() + timedelta(days=er_days)
        return Underlying(ticker.upper(), spot,
                          atr_wilder(highs, lows, closes, 14),
                          hist_vol(closes, 20),
                          hv_rank(closes, 20, 252),
                          atm_iv=atm_iv, next_earnings=nx)

    def get_chain(self, ticker, u, min_dte, max_dte):
        from datetime import timedelta
        import random
        rng = random.Random(self.seed + 7)
        out = []
        spot = u.spot
        # 幾個到期日
        for dte in (35, 45, 58):
            if dte < min_dte or dte > max_dte:
                continue
            exp = date.today() + timedelta(days=dte)
            T = dte / 365
            # strike 由 -25% 到 +25%,每 ~2.5% 一格
            step = max(1.0, round(spot * 0.025))
            k = round((spot * 0.75) / step) * step
            while k <= spot * 1.25:
                moneyness = math.log(k / spot)
                # IV smile:離 ATM 越遠 IV 越高;put skew
                smile = u.atm_iv * (1 + 1.8 * moneyness**2)
                for is_call in (True, False):
                    skew = 0.0 if is_call else 0.02 * max(0, -moneyness) * 10
                    iv = max(0.05, smile + skew)
                    g = bs_greeks(spot, k, dte, iv, r=self.r, is_call=is_call)
                    # 用 BS 理論價當 mid,加合理 spread / OI / vol
                    theo = self._bs_price(spot, k, dte, iv, is_call)
                    mid = max(0.02, theo)
                    spr = mid * rng.uniform(0.01, 0.05)
                    atm_factor = math.exp(-((k - spot) / (spot * 0.1))**2)
                    oi = int(3000 * atm_factor + rng.uniform(0, 400))
                    vol = int(800 * atm_factor + rng.uniform(0, 150))
                    c = OptionContract(
                        ticker.upper(), exp, dte, float(k), is_call,
                        bid=round(mid - spr / 2, 2), ask=round(mid + spr / 2, 2),
                        last=round(mid, 2), volume=vol, open_interest=oi, iv=iv,
                    )
                    c.greeks = g
                    out.append(c)
                k += step
        return out

    @staticmethod
    def _bs_price(S, K, dte, iv, is_call, r=0.045):
        T = dte / 365
        if T <= 0 or iv <= 0:
            return max(0.0, (S - K) if is_call else (K - S))
        d1 = (math.log(S / K) + (r + 0.5 * iv * iv) * T) / (iv * math.sqrt(T))
        d2 = d1 - iv * math.sqrt(T)
        if is_call:
            return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)
        return K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)


# ----------------------------------------------------------------------------
# 7) 輸出
# ----------------------------------------------------------------------------

def print_report(u: Underlying, side: str, top: list[Scored]):
    print("=" * 78)
    print(f"  {u.ticker}   現價 ${u.spot:.2f}   ATR(14)=${u.atr:.2f}   "
          f"HV20={u.hv20*100:.1f}%   HV-Rank={u.hv_rank:.0f}")
    iv_hv = (u.atm_iv / u.hv20) if (u.hv20 and not math.isnan(u.atm_iv)) else float('nan')
    er = u.next_earnings.isoformat() if u.next_earnings else "—"
    print(f"  ATM-IV={u.atm_iv*100:.1f}%   IV/HV={iv_hv:.2f}   "
          f"下次earnings={er}   →  方向建議: 【{side.upper()}】")
    print("-" * 78)
    if not top:
        print("  （冇合條件嘅候選:可能流動性/DTE/delta 過濾太緊,或無數據）")
        return
    for i, s in enumerate(top, 1):
        c = s.contract
        cp = "CALL" if c.is_call else "PUT"
        g = c.greeks
        print(f"  #{i}  {cp} {c.strike:g}  exp {c.expiry}  ({c.dte}d)   "
              f"分數={s.score:.1f}")
        print(f"       mid=${c.mid:.2f}  Δ={g.delta:+.2f}  Γ={g.gamma:.4f}  "
              f"θ/日=${g.theta_per_day:.3f}  vega/1%=${g.vega_per_1pct:.3f}  "
              f"IV={c.iv*100:.1f}%")
        for r in s.reasons:
            print(f"         • {r}")
    print()


def _safe(x):
    """NaN → None,方便 JSON。"""
    return None if (isinstance(x, float) and math.isnan(x)) else x


def result_to_dict(u: Underlying, side: str, top: list[Scored]) -> dict:
    iv_hv = (u.atm_iv / u.hv20) if (u.hv20 and not math.isnan(u.atm_iv)) else None
    picks = []
    for s in top:
        c, g = s.contract, s.contract.greeks
        picks.append({
            "type": "CALL" if c.is_call else "PUT",
            "strike": c.strike, "expiry": c.expiry.isoformat(), "dte": c.dte,
            "score": round(s.score, 1), "mid": round(c.mid, 2),
            "iv": round(c.iv, 4),
            "delta": round(g.delta, 3), "gamma": round(g.gamma, 4),
            "theta": round(g.theta_per_day, 3), "vega": round(g.vega_per_1pct, 3),
            "oi": c.open_interest, "volume": c.volume,
            "spread_pct": round(c.spread_pct, 3),
            "reasons": s.reasons,
        })
    return {
        "ticker": u.ticker, "spot": round(u.spot, 2),
        "atr": _safe(round(u.atr, 2) if not math.isnan(u.atr) else float("nan")),
        "hv20": _safe(round(u.hv20, 4) if not math.isnan(u.hv20) else float("nan")),
        "hv_rank": _safe(round(u.hv_rank, 0) if not math.isnan(u.hv_rank) else float("nan")),
        "atm_iv": _safe(round(u.atm_iv, 4) if not math.isnan(u.atm_iv) else float("nan")),
        "iv_hv": _safe(round(iv_hv, 2) if iv_hv is not None else None),
        "earnings": u.next_earnings.isoformat() if u.next_earnings else None,
        "side": side.upper(),
        "picks": picks,
    }


def export_json(path: str, results: list[dict], cfg: ScreenConfig, demo: bool):
    import json
    from datetime import timezone
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source": "DEMO(合成數據)" if demo else "LIVE",
        "config": {
            "min_dte": cfg.min_dte, "max_dte": cfg.max_dte,
            "min_oi": cfg.min_oi, "min_vol": cfg.min_vol,
            "max_spread_pct": cfg.max_spread_pct,
            "buy_delta": list(cfg.buy_delta), "sell_delta": list(cfg.sell_delta),
        },
        "results": results,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"已寫 JSON → {path}")
    # 同時寫一個 .js 版(全域變數),令網頁喺 file:// 本地開都讀到(免 CORS)
    if path.endswith(".json"):
        js_path = path[:-5] + ".js"
        with open(js_path, "w", encoding="utf-8") as f:
            f.write("window.OPTIONS_DATA = ")
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write(";\n")
        print(f"已寫 JS  → {js_path}")


def build_provider(args) -> DataProvider:
    if args.demo:
        return SampleProvider(r=args.rate)
    if args.tradier_token:
        return TradierProvider(args.tradier_token,
                               sandbox=not args.tradier_live, r=args.rate)
    return YFinanceProvider(r=args.rate)


def main(argv=None):
    p = argparse.ArgumentParser(description="ATR+IV+Greeks 期權 screener")
    p.add_argument("--tickers", nargs="+", required=True)
    p.add_argument("--side", choices=["auto", "buy", "sell"], default="auto")
    p.add_argument("--min-dte", type=int, default=30)
    p.add_argument("--max-dte", type=int, default=60)
    p.add_argument("--min-oi", type=int, default=500)
    p.add_argument("--min-vol", type=int, default=50)
    p.add_argument("--max-spread", type=float, default=0.06)
    p.add_argument("--top", type=int, default=5)
    p.add_argument("--rate", type=float, default=0.045)
    p.add_argument("--demo", action="store_true", help="用離線合成數據")
    p.add_argument("--tradier-token", default=None)
    p.add_argument("--tradier-live", action="store_true")
    p.add_argument("--json", default=None,
                   help="同時匯出結果做 JSON(畀 dashboard 網站用)")
    args = p.parse_args(argv)

    cfg = ScreenConfig(side=args.side, min_dte=args.min_dte,
                       max_dte=args.max_dte, min_oi=args.min_oi,
                       min_vol=args.min_vol, max_spread_pct=args.max_spread,
                       r=args.rate, top_n=args.top)
    provider = build_provider(args)

    print("\n⚠️  教育用途,非投資建議。"
          + ("  [DEMO:合成數據]" if args.demo else "  [LIVE 數據]") + "\n")
    results = []
    for tk in args.tickers:
        try:
            u, top = screen_ticker(provider, tk, cfg)
            side = decide_side(u, cfg)
            print_report(u, side, top)
            results.append(result_to_dict(u, side, top))
        except Exception as e:
            print(f"[{tk}] 出錯: {e}", file=sys.stderr)

    if args.json:
        export_json(args.json, results, cfg, args.demo)


if __name__ == "__main__":
    main()
