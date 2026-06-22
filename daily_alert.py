#!/usr/bin/env python3
"""
daily_alert.py  —  一撳就跑:篩選期權 + 寄 email 入你 Gmail
============================================================
唔使 GitHub。配合你部機嘅排程器(Windows Task Scheduler / Mac launchd / cron),
設定逢星期一至五 20:30 HKT 自動跑就得。

第一次用:
  1) 將 email_config.example.json 改名做 email_config.json
  2) 填入你嘅 Gmail App Password(見 README_options.md)
  3) 試跑:  python daily_alert.py
  4) 收到 email = 成功,跟住設排程(見下面 print 出嚟嘅提示)

注意:
  • 星期六日唔會寄(美股休市),自動略過。
  • 要有網先攞到報價(yfinance)。
  • email_config.json 已加入 .gitignore,唔會被 commit。
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "email_config.json")

# 預設標的(可喺 email_config.json 用 "tickers" 覆蓋)
DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA", "SPY", "QQQ", "AMD", "GOOGL", "META"]


def load_config():
    if not os.path.exists(CONFIG):
        print(f"⚠️ 搵唔到 {CONFIG}")
        print("   請將 email_config.example.json 改名做 email_config.json 並填好。")
        sys.exit(1)
    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    # 將 email 設定塞入環境變數,畀 notify.py 用
    for k in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS",
              "EMAIL_TO", "EMAIL_FROM", "SCORE_THRESHOLD", "ALERT_SIDES"):
        if cfg.get(k) not in (None, ""):
            os.environ[k] = str(cfg[k])
    return cfg


def is_us_trading_day():
    # 美東 weekday(避免 HK 已經星期六但美東仲係五嘅邊界,用美東日期)
    et = datetime.now(timezone.utc) - timedelta(hours=4)  # 粗略 ET(EDT)
    return et.weekday() < 5  # 0=一 .. 4=五


def main():
    cfg = load_config()
    tickers = cfg.get("tickers") or DEFAULT_TICKERS

    demo = bool(cfg.get("demo"))
    if not demo and not is_us_trading_day() and not cfg.get("force"):
        print("今日美股休市(週末),唔跑。想強制可喺 config 設 \"force\": true。")
        return

    # 跑 screener(直接呼叫,唔使 subprocess)
    sys.path.insert(0, HERE)
    import options_screener as scr
    import notify

    cfgs = scr.ScreenConfig(
        side="auto",
        min_dte=int(cfg.get("min_dte", 30)),
        max_dte=int(cfg.get("max_dte", 60)),
        top_n=int(cfg.get("top", 5)),
        r=float(cfg.get("rate", 0.045)),
    )
    if demo:
        print("【DEMO:合成數據,測試 email 用】")
        provider = scr.SampleProvider(r=cfgs.r)
        tickers = [t for t in tickers if t in scr.SampleProvider.PRESETS] or ["AAPL", "NVDA", "KO", "SPY"]
    else:
        provider = scr.YFinanceProvider(r=cfgs.r)

    print(f"篩緊:{' '.join(tickers)}")
    results = []
    for tk in tickers:
        try:
            u, top, chain = scr.screen_ticker(provider, tk, cfgs)
            side = scr.decide_side(u, cfgs)
            spreads = scr.build_spreads(chain, side, u.spot)
            results.append(scr.result_to_dict(u, side, top, spreads, cfgs.r))
            print(f"  ✓ {tk}: {side.upper()} ({len(top)} 候選)")
        except Exception as e:
            print(f"  ✗ {tk}: {e}", file=sys.stderr)

    # 寫埋 json + 歷史(畀 dashboard 用,順手)
    data_path = os.path.join(HERE, "options_data.json")
    scr.export_json(data_path, results, cfgs, demo=demo)
    scr.append_history(os.path.join(HERE, "options_history.json"), results)

    # 寄 email
    threshold = float(os.environ.get("SCORE_THRESHOLD", "80"))
    sides = {s.strip().upper()
             for s in os.environ.get("ALERT_SIDES", "BUY,SELL").split(",")}
    data = notify.load(data_path)
    alerts = notify.collect_alerts(data, threshold, sides)
    if not alerts:
        print(f"今日冇分數 ≥ {threshold} 嘅 setup,唔寄 email。")
        return
    msg = notify.fmt_message(data, alerts, threshold)
    top = max((p.get("score", 0) for r in data["results"]
               for p in r.get("picks", [])), default=0)
    subject = f"📈 期權提示:{len(alerts)} 個高分 setup(最高 {top})"
    if notify.send_email(msg, subject):
        print("✅ Email 已寄出。")
    else:
        print("⚠️ Email 未寄出:檢查 email_config.json 嘅 SMTP 設定。")


if __name__ == "__main__":
    main()
