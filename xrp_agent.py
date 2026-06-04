import sys, datetime, requests, os, json

GEMINI_API_KEY     = os.environ["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]
GITHUB_TOKEN       = os.environ["GITHUB_TOKEN"]
GITHUB_REPO        = os.environ["GITHUB_REPO"]

HOLDINGS = 13775
ENTRY    = 1.31
INVESTED = HOLDINGS * ENTRY

PROMPT = """אתה סוכן ניתוח מטבעות קריפטו מקצועי המתמחה ב-XRP/Ripple.
חפש באינטרנט נתונים עדכניים וצור סקירה יומית ממוקדת בעברית.

החזר תשובה בפורמט JSON בלבד, ללא טקסט נוסף, ללא קוד markdown:
{
  "price": 1.178,
  "change24h": -4.57,
  "changeWeek": -9.6,
  "rsi": 29,
  "rsi_signal": "מכירת יתר",
  "macd": "שלילי — חצייה דובית",
  "support1": 1.15,
  "support2": 1.00,
  "resist1": 1.25,
  "resist2": 1.38,
  "pattern": "משולש שבור מטה",
  "entry": 1.18,
  "sl": 1.14,
  "tp1": 1.25,
  "tp2": 1.38,
  "rr": "1:2.5",
  "fundamental": "תקציר פונדמנטלי של 3-4 משפטים על החדשות החשובות ביותר",
  "tweets": [
    {"user": "@שם", "text": "תוכן הציוץ"},
    {"user": "@שם", "text": "תוכן הציוץ"},
    {"user": "@שם", "text": "תוכן הציוץ"}
  ],
  "rumor": "שמועה חמה אחת מהקהילה",
  "upcoming": "אירוע צפוי אחד חשוב",
  "sentiment": 3,
  "sentiment_text": "פחד קיצוני",
  "recommendation": "HOLD",
  "rec_reason": "הסבר קצר של משפט אחד"
}"""


def get_xrp_data():
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    )
    today = datetime.date.today().strftime("%d/%m/%Y")
    payload = {
        "contents": [{"parts": [{"text": f"{PROMPT}\n\nתאריך היום: {today}"}]}],
        "tools": [{"google_search": {}}]
    }
    resp = requests.post(url, json=payload, timeout=60)
    if not resp.ok:
        raise Exception(f"Gemini error {resp.status_code}: {resp.text[:300]}")
    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def build_html(d, today):
    price    = d["price"]
    current  = HOLDINGS * price
    pnl      = current - INVESTED
    pnl_pct  = (pnl / INVESTED) * 100
    is_up    = pnl >= 0
    pnl_color = "#0F6E56" if is_up else "#A32D2D"
    arrow    = "▲" if is_up else "▼"
    progress = min(100, max(0, ((price - 0.80) / (2.00 - 0.80)) * 100))
    rec = d["recommendation"]
    rec_colors = {
        "STRONG BUY":  ("#E1F5EE","#085041"),
        "BUY":         ("#E1F5EE","#085041"),
        "HOLD":        ("#FAEEDA","#633806"),
        "SELL":        ("#FCEBEB","#791F1F"),
        "STRONG SELL": ("#FCEBEB","#791F1F"),
    }
    rc_bg, rc_fg = rec_colors.get(rec.upper(), ("#F1EFE8","#444441"))
    change_color = "#0F6E56" if d["change24h"] >= 0 else "#A32D2D"
    tweets_html = "".join(
        f'<div class="news-item"><strong>{t["user"]}</strong> — {t["text"]}</div>'
        for t in d.get("tweets", [])
    )

    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>XRP Dashboard — {today}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, Arial, sans-serif; background: #f5f5f0; color: #1a1a18; padding: 16px; direction: rtl; }}
  .dash {{ max-width: 700px; margin: 0 auto; }}
  .top-bar {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }}
  .top-bar h1 {{ font-size: 18px; font-weight: 600; }}
  .date {{ font-size: 12px; color: #888; }}
  .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 16px; }}
  @media(max-width:500px) {{ .metrics {{ grid-template-columns: repeat(2, 1fr); }} }}
  .metric {{ background: #fff; border-radius: 10px; padding: 12px 14px; border: 0.5px solid #e5e5e0; }}
  .metric .label {{ font-size: 11px; color: #888; margin-bottom: 4px; }}
  .metric .value {{ font-size: 20px; font-weight: 600; }}
  .metric .sub {{ font-size: 11px; color: #aaa; margin-top: 2px; }}
  .card {{ background: #fff; border: 0.5px solid #e5e5e0; border-radius: 12px; padding: 16px; margin-bottom: 14px; }}
  .card h2 {{ font-size: 13px; font-weight: 600; color: #666; margin-bottom: 12px; }}
  .row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 0.5px solid #f0f0ea; font-size: 13px; }}
  .row:last-child {{ border-bottom: none; }}
  .row .k {{ color: #888; }}
  .row .v {{ font-weight: 600; }}
  .sections {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  @media(max-width:500px) {{ .sections {{ grid-template-columns: 1fr; }} }}
  .news-item {{ padding: 7px 0; border-bottom: 0.5px solid #f0f0ea; font-size: 12px; color: #666; line-height: 1.5; }}
  .news-item:last-child {{ border-bottom: none; }}
  .news-item strong {{ color: #1a1a18; font-weight: 600; }}
  .progress-bar {{ height: 8px; background: #f0f0ea; border-radius: 4px; overflow: hidden; margin: 8px 0 4px; }}
  .progress-fill {{ height: 100%; border-radius: 4px; }}
  .tag {{ display: inline-flex; padding: 4px 12px; border-radius: 8px; font-size: 13px; font-weight: 700; }}
  .bottom-bar {{ display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: #fff; border-radius: 10px; border: 0.5px solid #e5e5e0; }}
  a.chart-link {{ color: #185FA5; font-size: 12px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; margin-top: 8px; }}
  .sent-bar {{ display: flex; align-items: center; gap: 8px; margin-top: 8px; }}
  .sent-track {{ flex: 1; height: 6px; background: #f0f0ea; border-radius: 3px; overflow: hidden; }}
</style>
</head>
<body>
<div class="dash">
  <div class="top-bar">
    <h1>◎ XRP Dashboard</h1>
    <span class="date">עודכן: {today}</span>
  </div>

  <div class="metrics">
    <div class="metric">
      <div class="label">מחיר נוכחי</div>
      <div class="value" style="color:{change_color}">${price:.3f}</div>
      <div class="sub" style="color:{change_color}">{arrow} {abs(d['change24h']):.2f}% היום</div>
    </div>
    <div c
