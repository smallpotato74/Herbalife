#!/usr/bin/env python3
"""
notify.py
=========
讀 options_data.json,當有高分 setup(分數 >= 門檻)就發通知。
支援 Telegram / Email(SMTP) / 通用 Webhook(Discord/Slack)。全部靠環境變數,
冇設定就靜靜略過,唔會出錯。配合 GitHub Actions 每日跑。

環境變數
--------
SCORE_THRESHOLD      預設 80。分數 >= 呢個先通知。
ALERT_SIDES          預設 "BUY,SELL"。只想其中一邊就改。

Telegram:
  TELEGRAM_BOT_TOKEN   問 @BotFather 攞
  TELEGRAM_CHAT_ID     你同個 bot 傾偈後,睇 getUpdates 攞 chat id

Email(SMTP):
  SMTP_HOST SMTP_PORT SMTP_USER SMTP_PASS  EMAIL_TO  (EMAIL_FROM 可選)

通用 Webhook(Discord/Slack incoming webhook):
  WEBHOOK_URL          POST {"content"/"text": msg}

用法: python notify.py [options_data.json]
"""
import json
import os
import sys
import urllib.request


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect_alerts(data, threshold, sides):
    out = []
    for r in data.get("results", []):
        if r.get("side") not in sides:
            continue
        for p in r.get("picks", []):
            if p.get("score", 0) >= threshold:
                pop = (p.get("pnl") or {}).get("pop")
                out.append(
                    f"• {r['ticker']} {r['side']} {p['type']} {p['strike']} "
                    f"({p['dte']}d) 分{p['score']} "
                    f"Δ{p['delta']} IV{p['iv']*100:.0f}%"
                    + (f" POP{pop}%" if pop is not None else "")
                )
    return out


def fmt_message(data, alerts, threshold):
    head = (f"📈 期權高分提示(分數≥{threshold})  {data.get('generated_at','')}\n"
            f"來源:{data.get('source','')}\n")
    return head + "\n".join(alerts) + "\n\n⚠️ 教育用途,非投資建議。"


def _post(url, payload, headers=None):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data,
                                 headers=headers or {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.status


def send_telegram(msg):
    tok, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not (tok and chat):
        return False
    url = f"https://api.telegram.org/bot{tok}/sendMessage"
    _post(url, {"chat_id": chat, "text": msg, "disable_web_page_preview": True})
    print("→ Telegram 已發")
    return True


def send_webhook(msg):
    url = os.getenv("WEBHOOK_URL")
    if not url:
        return False
    # Discord 用 content;Slack 用 text。兩個 key 都俾,對方取自己嗰個。
    _post(url, {"content": msg, "text": msg})
    print("→ Webhook 已發")
    return True


def send_email(msg, subject="期權高分提示"):
    host = os.getenv("SMTP_HOST")
    to = os.getenv("EMAIL_TO")
    if not (host and to):
        return False
    import smtplib
    from email.mime.text import MIMEText
    m = MIMEText(msg, "plain", "utf-8")
    m["Subject"] = subject
    m["From"] = os.getenv("EMAIL_FROM", os.getenv("SMTP_USER", "options-bot"))
    m["To"] = to
    port = int(os.getenv("SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=20) as s:
        s.starttls()
        if os.getenv("SMTP_USER"):
            s.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS", ""))
        s.send_message(m)
    print("→ Email 已發")
    return True


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "options_data.json"
    threshold = float(os.getenv("SCORE_THRESHOLD", "80"))
    sides = {s.strip().upper() for s in os.getenv("ALERT_SIDES", "BUY,SELL").split(",")}
    try:
        data = load(path)
    except FileNotFoundError:
        print(f"搵唔到 {path},略過通知。")
        return
    alerts = collect_alerts(data, threshold, sides)
    if not alerts:
        print(f"冇分數 ≥ {threshold} 嘅 setup,唔發通知。")
        return
    msg = fmt_message(data, alerts, threshold)
    print(msg)
    # 主旨整靚:有幾多個 + 最高分,Gmail inbox 一眼睇到
    top = max((p.get("score", 0) for r in data.get("results", [])
               for p in r.get("picks", [])), default=0)
    subject = f"📈 期權提示:{len(alerts)} 個高分 setup(最高 {top})"
    sent = any([send_telegram(msg), send_webhook(msg),
                send_email(msg, subject)])
    if not sent:
        print("(未設定任何通知渠道;設定 TELEGRAM_* / WEBHOOK_URL / SMTP_* 環境變數即可。)")


if __name__ == "__main__":
    main()
