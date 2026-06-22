# Options Trading 策略報告：用 ATR + IV + Gamma 篩選高質期權

> ⚠️ **免責聲明**：本文件純屬教育及研究用途，唔構成任何投資建議。期權有高槓桿同高風險，可以蝕足本金甚至超出本金（short naked 嘅情況）。落場前請用模擬倉練熟，並控制好倉位大小。

---

## 0. 一頁速覽（TL;DR）

| 你想做 | 條件（簡化版） | 核心邏輯 |
|---|---|---|
| **Buy Call / Buy Put**（做長 / 做空方向） | IV Rank **偏低**（< 30）、近期會有催化劑、ATR 上升 | 你係買波動，要喺平嘅時候買，等股價同 IV 一齊升 |
| **Short Call / Short Put**（沽期權收 premium） | IV Rank **偏高**（> 50）、Gamma 唔好太大、DTE 30–45 日 | 你係賣保險，要喺貴嘅時候賣，等 IV 同 time value 萎縮 |
| **進階 Spread**（垂直 / Iron Condor / Calendar） | 用嚟限制風險、隔離你想賺嘅 Greek | 唔使裸沽，risk defined |

**一句心法**：
- **方向睇 ATR**（呢隻嘢郁唔郁、夠唔夠空間到價）
- **平定貴睇 IV**（你係買保險定賣保險）
- **節奏／加速度睇 Gamma**（接近到期 + 接近 strike，Gamma 爆，P&L 會好癲）

---

## 1. 三個核心指標係咩，點解有用

### 1.1 ATR（Average True Range）— 量度「股票本身嘅波幅」

ATR 係過去 N 日（通常 14 日）嘅平均真實波幅，用 **股價單位**（蚊）表示。

**True Range = max 嘅以下三者：**
1. 今日 High − 今日 Low
2. |今日 High − 昨日 Close|
3. |今日 Low − 昨日 Close|

ATR 就係呢個 TR 嘅平均（多數用 Wilder smoothing）。

**期權點用：**
- **判斷 target 到唔到價**：如果一隻股 ATR = $3，你買一個 OTM call，行使價離現價 $9（即 3 個 ATR），理論上要 3 日「全力向上」先掂到，機會偏低 → 唔抵買。
- **設止賺止蝕**：用 1.5×–2× ATR 做股價層面嘅 stop，再換算返期權價。
- **ATR 上升 = realized volatility 上升**，對 long option 有利（你揸住嘅嘢開始郁）。

> 實用比例：**揀 strike 嘅距離 ≤ 1–1.5 個 ATR ×（到期日數）** 比較有勝算。

### 1.2 IV（Implied Volatility）— 量度「期權貴唔貴」

IV 係市場用期權價反推返出嚟嘅「預期未來波幅」。**重點唔係 IV 嘅絕對數值，而係佢相對自己歷史係高定低。**

**要睇嘅係：**
- **IV Rank (IVR)** = (現時 IV − 一年最低 IV) / (一年最高 IV − 一年最低 IV) × 100
  - IVR = 0 → 一年嚟最平
  - IVR = 100 → 一年嚟最貴
- **IV Percentile**：過去一年有幾多 % 嘅日子 IV 低過今日（比 IVR 更穩陣，少受極端值影響）。

**期權點用（最重要一條規矩）：**
- **IVR 低（< 30）→ 偏向 BUY**（long call / put / debit spread）：期權平，買咗如果 IV 升你仲賺埋 vega。
- **IVR 高（> 50）→ 偏向 SELL**（short put / call / credit spread / iron condor）：期權貴，賣咗等 IV 回落（**IV crush**）你賺 vega + theta。

**IV Crush 陷阱**：業績（earnings）前 IV 會炒到好高，業績一出 IV 即刻塌。所以業績前 **buy** option 好多時就算估啱方向都蝕（因為 IV crush 食晒你嘅利潤）。要食 earnings 通常係 **sell** vol（但風險大，要 defined risk）。

### 1.3 Gamma — 量度「Delta 變得幾快」（加速度）

- **Delta** = 期權價對股價嘅一階敏感度（你嘅「即時方向曝險」）。
- **Gamma** = Delta 對股價嘅變化率（二階）。Gamma 大 = 股價郁少少，Delta 就跳好多。

**Gamma 嘅特性：**
- **ATM（平價）+ 接近到期** → Gamma 最大。
- Gamma 對 **long option 係朋友**（股價向你郁時，賺得加速；向你逆時，蝕得減速）。
- Gamma 對 **short option 係敵人**（即 negative gamma：逆你嘅時候蝕到加速，呢個就係 short gamma 嘅惡夢，例如 short 0DTE）。

**Gamma vs Theta 嘅交換**：高 gamma 一定伴隨高 theta（時間損耗快）。你 long gamma = 你要每日俾 theta「租金」，換取股價郁時嘅爆發力。Short gamma 啱啱相反：收 theta 租金，但要承受 gamma 風險。

---

## 2. 篩選「高質期權」嘅流程（Screener Checklist）

一個 trade 由上至下逐層過濾：

### Step 1 — 流動性（唔過呢關直接 skip）
- **Open Interest** ≥ 500（個別大股可以更高要求）
- **Volume** 當日 ≥ 100
- **Bid-Ask Spread** ≤ 報價嘅 5%（spread 闊 = 一入場就輸喺摩擦成本）
- 揀 **monthly / weekly 主流到期日**，唔好揀啲冇人交易嘅日子

### Step 2 — 用 IVR 決定「方向：買定賣」
```
IVR < 30  → 買方陣營（long premium）
IVR 30–50 → 中性，傾向用 spread / 觀望
IVR > 50  → 賣方陣營（short premium / credit）
```

### Step 3 — 用 ATR 決定「strike 同 target」
- 計 **預期到價空間 = ATR × √(DTE)**（粗略 scaling，因波動隨時間開根號擴散）
- 買方：揀嘅 strike 距離 **唔好超過** 呢個預期空間，否則勝率太低
- 賣方：揀嘅 short strike 距離 **大過** 1×（最好 1.5×）呢個預期空間 → 安全邊際足

### Step 4 — 用 Delta 揀 strike（實用代理）
| 用途 | Delta 範圍 | 意思 |
|---|---|---|
| Buy 方向倉（要槓桿但唔太博彩） | 0.55–0.70 | ITM 少少，delta 高，受 theta/IV 影響細 |
| Buy 博爆發（小注博大） | 0.25–0.40 | OTM，便宜但勝率低 |
| Sell premium（高勝率收租） | 0.15–0.30 | OTM，約 70–85% 機會 expire worthless |

### Step 5 — 用 Gamma / DTE 控制節奏
- **Buy 方向**：揀 **DTE 45–90 日**，gamma 唔好太癲，俾時間個 thesis 發酵，theta 慢
- **Sell premium**：揀 **DTE 30–45 日**（theta 衰減最甜嘅區間），到 **21 DTE 或收咗 50% 利潤就走**，避開到期前 gamma 爆煲
- **避免**：buy 短 DTE（< 14 日）除非你係短炒 + 有明確催化劑；sell 0DTE/極短 DTE 除非你好識管理 gamma

### Step 6 — 催化劑日曆
- 睇清楚 **earnings / Fed / CPI / 除淨** 日期
- Buy：想喺催化劑 **之前** IV 仲未炒起時入（賺 vega + 方向）
- Sell：earnings 係雙刃劍，要做就用 **defined-risk**（iron condor / credit spread），唔好裸沽

---

## 3. 四種基本倉位 + 進出場時機

下面每種都俾你 **入場條件 / strike 揀法 / 止賺 / 止蝕 / 時間止損**。

### 3.1 Buy Call（睇升，買升）
**幾時用**：睇好方向 + IVR 低 + 有上升催化劑 + ATR 開始放大。

- **入場**：
  - IVR < 30
  - 股價企穩支持位 / 突破阻力 + 成交量配合
  - Delta 0.55–0.70（要 leverage 但唔好太博）
  - DTE 45–90 日
- **止賺**：
  - 賺到 **50–100%** premium，或股價到你用 ATR 計嘅 target
  - 分注走：到第一個 target 走一半，餘下用 trailing stop
- **止蝕**：
  - 蝕 **40–50%** premium 就走（期權唔好幻想會返家鄉）
  - 或股價跌穿入場時嘅 1.5× ATR stop
- **時間止損**：到 **21 DTE** 如果仲未 work，theta 開始咬，考慮平倉換月

### 3.2 Buy Put（睇跌，買跌）
同 Buy Call 鏡像，方向相反。

- **入場**：IVR 低、股價跌穿支持 / 形成見頂、避險需求升、ATR 放大
- **注意**：跌市時 IV 通常會急升 → put 嘅 vega 幫到你，但亦代表你可能要追貴貨。最理想係 **跌勢初段、IV 未爆** 入場
- 止賺 / 止蝕 / 時間止損同 Buy Call 一樣邏輯

### 3.3 Short Put（睇唔跌 / 想低位接貨，沽 put 收租）
**幾時用**：IVR 高 + 你願意喺 short strike 價接呢隻股 + 唔預佢大跌。

- **入場**：
  - IVR > 50
  - Short strike Delta 0.15–0.30（OTM，距離 > 1.5× ATR 預期空間）
  - DTE 30–45 日
- **止賺**：收咗 **50% premium** 就平（tastytrade 經典機械式法則），唔好貪到尾
- **止蝕**：蝕到 **2× 收到嘅 premium** 就走；或股價跌穿 short strike 要決定 roll 定接貨
- **時間止損**：到 **21 DTE** 無論輸贏都管理（roll 落下個月或平倉），避 gamma risk
- **進階**：可以變 **cash-secured put**（有錢接貨）或做 **put credit spread**（買多隻更遠 put 封頂風險）

### 3.4 Short Call（睇唔升，沽 call 收租）— ⚠️ 最危險
**幾時用**：IVR 高 + 強阻力 + 你預個價上唔到。

- ⚠️ **裸 short call 風險無限**（股票可以無上限咁升），新手 **唔好裸沽**，一定要做 **call credit spread** 或 **covered call**（你已經揸住正股）
- **入場**：IVR > 50、short strike Delta 0.15–0.25、DTE 30–45 日
- **止賺 / 止蝕 / 時間**：同 short put 對稱（50% 止賺、2× 止蝕、21 DTE 管理）

---

## 4. 進階玩法（你問「更進階」嘅部分）

### 4.1 由「裸倉」升級去「Spread」— 隔離你想賺嘅嘢
裸 long / short option 你會同時食晒方向（delta）、波動（vega）、時間（theta）。Spread 可以幫你 **淨化** 想要嘅曝險、限制風險：

| 策略 | 結構 | 啱咩情況 | 主要賺 |
|---|---|---|---|
| **Bull Call Spread**（debit） | 買低 strike call + 沽高 strike call | 溫和睇升 + 想慳成本/降 IV 曝險 | 方向 |
| **Bull Put Spread**（credit） | 沽高 strike put + 買低 strike put | 睇唔跌 + IVR 高 | theta + vega |
| **Iron Condor** | 同時做 put credit + call credit spread | 預個價 **橫行** + IVR 高 | theta + vega（vol 收縮） |
| **Calendar Spread** | 沽近月 + 買遠月（同 strike） | 預短期橫行、長期有 vol | term structure + theta |
| **Diagonal / PMCC** | 買深 ITM 遠月 call 當正股，逐月沽近月 call | 想低成本做 covered call | theta（每月收租） |

### 4.2 進階指標：唔止睇單一 Greek

- **Vega 管理**：你嘅組合對 IV 嘅總曝險。IVR 高想做淨 **short vega**（賣貴 vol）；IVR 低想 long vega。
- **IV Skew（垂直 skew）**：同一到期，唔同 strike 嘅 IV 唔同。通常 put 嘅 IV 高過 call（避險需求）。**Skew 偏斜** 可以揾 relative value（沽貴嗰邊、買平嗰邊，例如 risk reversal）。
- **Term Structure（橫向）**：近月 IV vs 遠月 IV。
  - **Contango**（遠月 > 近月）：正常市
  - **Backwardation**（近月 > 遠月）：通常市場恐慌 / 有近期事件 → calendar / diagonal 嘅機會
- **Volatility Risk Premium (VRP)**：歷史上 **IV 系統性高過之後 realized vol**，所以長期 systematically short vol（有風控）係有 edge 嘅，但會有「執硬幣前面壓路機」嘅尾部風險，必須 defined risk。
- **Dealer Gamma Exposure (GEX)**：市場層面，當 dealer net long gamma → 佢哋會「逆勢對沖」令大市波幅收細（pinning）；net short gamma → 「順勢對沖」放大波幅。可以幫你判斷大市係會 mean-revert 定加速。（呢個係進階宏觀 context，唔係必須）

### 4.3 進場時機（Timing）綜合決策樹
```
1. 揀標的：流動性過關？有冇催化劑？
2. 睇 IVR：
     低 → 買方思路（long premium / debit spread）
     高 → 賣方思路（short premium / credit / condor）
3. 睇方向（技術面 + ATR）：
     有方向 → 用 call/put 或 vertical spread 表達
     冇方向（橫行）→ iron condor / calendar
4. 睇 ATR 計到價空間 → 決定 strike 距離
5. 睇 DTE/Gamma：
     買方向 45–90 DTE
     賣 premium 30–45 DTE
6. 確認 entry trigger（突破/回踩支持/RSI 背馳 等），先扣扳機
```

### 4.4 退場時機（Exit）— 機械化先做得長
- **利潤目標**：買方 +50~100% 走；賣方收 50% premium 走
- **止蝕**：買方 −40~50% 走；賣方 蝕到 2× credit 走
- **時間**：到 **21 DTE** 一律重新評估（賣方尤其重要，避 gamma）
- **IV 觸發**：賣方倉如果 IVR 由高跌返落低位（vega 已賺到）→ 提早收割
- **Delta 觸發**：short strike 被 delta 升穿（例如 short put delta 升到 0.30→0.45）→ roll 或平
- **永遠唔好**：溝淡一個輸緊嘅裸 long option（time decay 會繼續食你）

---

## 5. 風險管理（呢段先係能唔能夠生存嘅關鍵）

1. **單一 trade 風險 ≤ 賬戶 1–3%**（buy option 用權利金做風險；short option 用最大潛在虧損做風險）
2. **組合 Greeks 上限**：set 一個你舒服嘅 net delta / net vega 範圍，唔好 all-in 單一方向
3. **分散到期日（laddering）**：唔好所有倉同一日到期，避免 gamma/event 集中
4. **避開 earnings 裸買**（IV crush）；要玩 earnings 用 defined-risk
5. **流動性永遠優先**：闊 spread 嘅嘢，止蝕嗰刻先發現走唔到
6. **記交易日誌**：記低入場理由（IVR / ATR / Delta / DTE / 催化劑）同結果，先進步得到

---

## 6. 如果想自動化／量化呢個 screener（落地建議）

如果你想將上面變成一個會跑數嘅 report / screener，可以咁起步：

**資料來源**：
- 期權鏈 + Greeks + IV：券商 API（IBKR / Tradier）、或數據商（ORATS, CBOE, Polygon.io）
- 股價 OHLC（計 ATR）：yfinance / Polygon / Alpha Vantage

**核心計算（pseudo / 模組）**：
```python
# 1) ATR
def atr(highs, lows, closes, period=14):
    tr = [max(h-l, abs(h-pc), abs(l-pc))
          for h, l, pc in zip(highs[1:], lows[1:], closes[:-1])]
    # Wilder smoothing
    a = sum(tr[:period]) / period
    for t in tr[period:]:
        a = (a*(period-1) + t) / period
    return a

# 2) IV Rank
def iv_rank(current_iv, iv_1y_high, iv_1y_low):
    return (current_iv - iv_1y_low) / (iv_1y_high - iv_1y_low) * 100

# 3) 預期到價空間（用 ATR scale）
def expected_move(atr_value, dte):
    return atr_value * (dte ** 0.5)

# 4) 篩選器（概念）
def screen(option, stock):
    if option.open_interest < 500: return None
    if option.bid_ask_spread_pct > 0.05: return None
    ivr = iv_rank(stock.iv, stock.iv_high, stock.iv_low)
    em = expected_move(stock.atr, option.dte)
    side = "BUY" if ivr < 30 else "SELL" if ivr > 50 else "NEUTRAL"
    # 距離 strike 同 expected move 比較 → 評分
    ...
    return score
```

**Scoring（綜合評分）概念**：
- 流動性分（OI / spread）
- IVR 分（買方俾低 IVR 高分；賣方俾高 IVR 高分）
- ATR-strike 配合度分（買方：strike 喺 expected move 內；賣方：strike 喺 expected move 外）
- Delta 落喺目標區間嘅分
- DTE 落喺目標區間嘅分
- 催化劑加 / 減分（earnings 前 buy 要扣分）

排個總分由高到低，就係你嘅「高質期權」清單。

---

## 7. 名詞快速對照表

| 詞 | 中文 | 一句講解 |
|---|---|---|
| ATR | 平均真實波幅 | 隻股每日平均郁幾多蚊 |
| IV | 引伸波幅 | 期權貴唔貴（市場預期波幅） |
| IVR / IV Percentile | IV 排名 / 百分位 | IV 相對自己一年係高定低 |
| Delta | — | 股價郁 $1 期權郁幾多；亦近似「價內機率」 |
| Gamma | — | Delta 嘅變化率（加速度） |
| Theta | — | 每過一日時間值蝕幾多 |
| Vega | — | IV 升 1% 期權升幾多 |
| DTE | 距到期日數 | Days To Expiration |
| IV Crush | IV 崩塌 | 事件後 IV 急跌，殺 long option |
| Credit / Debit | 收 / 俾 權利金 | 賣方收錢開倉 / 買方俾錢開倉 |

---

### 落地下一步建議
1. 揀 3–5 隻你熟、流動性高嘅標的（例如大型 ETF / 龍頭股）做觀察名單
2. 每隻紀錄：IVR、ATR、近期催化劑
3. 先用 **模擬倉** 跑齊上面流程 1–2 個月，校準你嘅 strike / DTE 偏好
4. 之後先用細注（1% 風險）實戰，嚴守機械化止賺止蝕

> 如果你想，我可以再幫你：
> - 寫一個 **可運行嘅 Python screener**（接 yfinance / Tradier API）
> - 整一個 **Excel / Google Sheet 模板** 自動計 IVR、ATR、expected move、評分
> - 針對 **某幾隻具體標的** 行一次完整篩選示範
