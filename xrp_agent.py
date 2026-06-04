import sys, datetime, requests, os, json

GEMINI_API_KEY     = os.environ["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]
GITHUB_TOKEN       = os.environ["GH_TOKEN"]
GITHUB_REPO        = os.environ["GH_REPO"]

HOLDINGS = 13775
ENTRY    = 1.31
INVESTED = HOLDINGS * ENTRY
ALERT_THRESHOLD = 0.05  # 5% move triggers alert

PROMPT = """You are a professional crypto analyst specializing in XRP/Ripple.
Search the internet for live data and return a daily briefing as JSON only.
No markdown, no extra text — pure JSON:
{
  "price": 1.178,
  "change24h": -4.57,
  "changeWeek": -9.6,
  "rsi": 29,
  "rsi_signal": "Oversold",
  "macd": "Negative — bearish crossover",
  "support1": 1.15,
  "support2": 1.00,
  "resist1": 1.25,
  "resist2": 1.38,
  "pattern": "Symmetrical triangle breakdown",
  "entry": 1.18,
  "sl": 1.14,
  "tp1": 1.25,
  "tp2": 1.38,
  "rr": "1:2.5",
  "fundamental": "3-4 sentence summary of the most important news in the last 48h",
  "tweets": [
    {"user": "@handle", "text": "tweet content"},
    {"user": "@handle", "text": "tweet content"},
    {"user": "@handle", "text": "tweet content"}
  ],
  "rumor": "One hot rumor circulating in the community",
  "upcoming": "One important upcoming event",
  "sentiment": 3,
  "sentiment_text": "Extreme Fear",
  "recommendation": "HOLD",
  "rec_reason": "One sentence explanation"
}"""


def get_xrp_data():
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    )
    today = datetime.date.today().strftime("%d/%m/%Y")
    payload = {
        "contents": [{"parts": [{"text": f"{PROMPT}\n\nToday's date: {today}"}]}],
        "tools": [{"google_search": {}}]
    }
    resp = requests.post(url, json=payload, timeout=60)
    if not resp.ok:
        raise Exception(f"Gemini error {resp.status_code}: {resp.text[:300]}")
    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])


def build_html(d, today):
    price     = d["price"]
    current   = HOLDINGS * price
    pnl       = current - INVESTED
    pnl_pct   = (pnl / INVESTED) * 100
    is_up     = pnl >= 0
    pnl_color = "#0F6E56" if is_up else "#A32D2D"
    arrow     = "▲" if is_up else "▼"
    progress  = min(100, max(0, ((price - 0.80) / (2.00 - 0.80)) * 100))
    ch_color  = "#0F6E56" if d["change24h"] >= 0 else "#A32D2D"
    rec = d["recommendation"].upper()
    rec_styles = {
        "STRONG BUY":  ("#E1F5EE","#085041"),
        "BUY":         ("#E1F5EE","#085041"),
        "HOLD":        ("#FAEEDA","#633806"),
        "SELL":        ("#FCEBEB","#791F1F"),
        "STRONG SELL": ("#FCEBEB","#791F1F"),
    }
    rc_bg, rc_fg = rec_styles.get(rec, ("#F1EFE8","#444441"))
    sent_color = "#0F6E56" if d["sentiment"] >= 6 else ("#E24B4A" if d["sentiment"] <= 3 else "#BA7517")
    tweets_html = "".join(
        f'<div class="news-item"><strong>{t["user"]}</strong> — {t["text"]}</div>'
        for t in d.get("tweets", [])
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>XRP Dashboard — {today}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, Arial, sans-serif; background: #f5f5f0; color: #1a1a18; padding: 16px; }}
  .dash {{ max-width: 700px; margin: 0 auto; }}
  .top-bar {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 0.5px solid #e5e5e0; }}
  .top-bar h1 {{ font-size: 20px; font-weight: 700; letter-spacing: -0.5px; }}
  .date {{ font-size: 12px; color: #888; }}
  .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 14px; }}
  @media(max-width:500px) {{ .metrics {{ grid-template-columns: repeat(2, 1fr); }} }}
  .metric {{ background: #fff; border-radius: 10px; padding: 12px 14px; border: 0.5px solid #e5e5e0; }}
  .metric .label {{ font-size: 11px; color: #888; margin-bottom: 4px; text-transform: uppercase; letter-spacing: .3px; }}
  .metric .value {{ font-size: 20px; font-weight: 700; }}
  .metric .sub {{ font-size: 11px; color: #aaa; margin-top: 2px; }}
  .card {{ background: #fff; border: 0.5px solid #e5e5e0; border-radius: 12px; padding: 16px; margin-bottom: 12px; }}
  .card h2 {{ font-size: 12px; font-weight: 700; color: #888; margin-bottom: 12px; text-transform: uppercase; letter-spacing: .5px; }}
  .row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 0.5px solid #f0f0ea; font-size: 13px; }}
  .row:last-child {{ border-bottom: none; }}
  .row .k {{ color: #888; }}
  .row .v {{ font-weight: 600; }}
  .sections {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  @media(max-width:500px) {{ .sections {{ grid-template-columns: 1fr; }} }}
  .news-item {{ padding: 7px 0; border-bottom: 0.5px solid #f0f0ea; font-size: 12px; color: #555; line-height: 1.5; }}
  .news-item:last-child {{ border-bottom: none; }}
  .news-item strong {{ color: #1a1a18; font-weight: 700; }}
  .progress-wrap {{ margin: 12px 0 4px; }}
  .progress-labels {{ display: flex; justify-content: space-between; font-size: 10px; color: #aaa; margin-bottom: 4px; }}
  .progress-bar {{ height: 8px; background: #f0f0ea; border-radius: 4px; overflow: hidden; }}
  .progress-fill {{ height: 100%; border-radius: 4px; }}
  .progress-note {{ font-size: 11px; color: #aaa; text-align: center; margin-top: 4px; }}
  .tag {{ display: inline-flex; padding: 5px 14px; border-radius: 8px; font-size: 13px; font-weight: 800; letter-spacing: .5px; }}
  .bottom-bar {{ display: flex; align-items: center; gap: 12px; padding: 14px 16px; background: #fff; border-radius: 10px; border: 0.5px solid #e5e5e0; margin-top: 4px; }}
  a.chart-link {{ color: #185FA5; font-size: 12px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; margin-top: 10px; font-weight: 600; }}
  .sent-row {{ display: flex; align-items: center; gap: 10px; margin-top: 10px; }}
  .sent-track {{ flex: 1; height: 6px; background: #f0f0ea; border-radius: 3px; overflow: hidden; }}
  .up {{ color: #0F6E56; }} .down {{ color: #A32D2D; }}
  .footer {{ text-align: center; font-size: 11px; color: #ccc; margin-top: 20px; }}
</style>
</head>
<body>
<div class="dash">
  <div class="top-bar">
    <h1>◎ XRP Dashboard</h1>
    <span class="date">Updated: {today}</span>
  </div>

  <div class="metrics">
    <div class="metric">
      <div class="label">Current Price</div>
      <div class="value" style="color:{ch_color}">${price:.3f}</div>
      <div class="sub" style="color:{ch_color}">{'▲' if d['change24h']>=0 else '▼'} {abs(d['change24h']):.2f}% today</div>
    </div>
    <div class="metric">
      <div class="label">My Investment</div>
      <div class="value">${INVESTED:,.0f}</div>
      <div class="sub">13,775 XRP · avg $1.31</div>
    </div>
    <div class="metric">
      <div class="label">Current Value</div>
      <div class="value">${current:,.0f}</div>
      <div class="sub" style="color:{pnl_color}">{arrow} ${abs(pnl):,.0f}</div>
    </div>
    <div class="metric">
      <div class="label">P&L</div>
      <div class="value" style="color:{pnl_color}">{pnl_pct:+.2f}%</div>
      <div class="sub" style="color:{pnl_color}">{'+' if is_up else '-'}${abs(pnl):,.0f}</div>
    </div>
  </div>

  <div class="card">
    <h2>Position Analysis — 13,775 XRP</h2>
    <div class="row"><span class="k">Total Invested</span><span class="v">${INVESTED:,.0f}</span></div>
    <div class="row"><span class="k">Current Value</span><span class="v">${current:,.0f}</span></div>
    <div class="row"><span class="k">Profit / Loss</span><span class="v" style="color:{pnl_color}">{'+' if is_up else ''}{pnl:,.0f}$ ({pnl_pct:+.2f}%)</span></div>
    <div class="row"><span class="k">Break-even</span><span class="v">$1.31 ({((1.31-price)/price*100):+.1f}% from here)</span></div>
    <div class="row"><span class="k">TP1 — $1.31 (break-even)</span><span class="v up">+${HOLDINGS*(1.31-price):,.0f} ({(1.31-price)/price*100:+.1f}%)</span></div>
    <div class="row"><span class="k">TP2 — $1.60</span><span class="v up">+${HOLDINGS*(1.60-price):,.0f} ({(1.60-price)/price*100:+.1f}%)</span></div>
    <div class="row"><span class="k">TP3 — $2.00</span><span class="v up">+${HOLDINGS*(2.00-price):,.0f} ({(2.00-price)/price*100:+.1f}%)</span></div>
    <div class="progress-wrap">
      <div class="progress-labels"><span>$0.80</span><span>Entry $1.31</span><span>$2.00</span></div>
      <div class="progress-bar"><div class="progress-fill" style="width:{progress:.0f}%;background:{pnl_color};"></div></div>
      <div class="progress-note">${price:.3f} — {progress:.0f}% of the way to $2.00</div>
    </div>
  </div>

  <div class="sections">
    <div class="card">
      <h2>Technical Analysis</h2>
      <div class="row"><span class="k">RSI</span><span class="v {'down' if d['rsi']<40 else 'up' if d['rsi']>60 else ''}">{d['rsi']} — {d['rsi_signal']}</span></div>
      <div class="row"><span class="k">MACD</span><span class="v">{d['macd']}</span></div>
      <div class="row"><span class="k">Support 1</span><span class="v">${d['support1']}</span></div>
      <div class="row"><span class="k">Support 2</span><span class="v">${d['support2']}</span></div>
      <div class="row"><span class="k">Resistance 1</span><span class="v">${d['resist1']}</span></div>
      <div class="row"><span class="k">Pattern</span><span class="v">{d['pattern']}</span></div>
      <a class="chart-link" href="https://www.tradingview.com/chart/?symbol=XRPUSDT">Live Chart — TradingView ↗</a>
    </div>

    <div class="card">
      <h2>Entry Points</h2>
      <div class="row"><span class="k">Entry</span><span class="v">${d['entry']}</span></div>
      <div class="row"><span class="k">Stop Loss</span><span class="v down">${d['sl']}</span></div>
      <div class="row"><span class="k">TP1</span><span class="v up">${d['tp1']}</span></div>
      <div class="row"><span class="k">TP2</span><span class="v up">${d['tp2']}</span></div>
      <div class="row"><span class="k">Risk / Reward</span><span class="v">{d['rr']}</span></div>
    </div>

    <div class="card" style="grid-column:1/-1">
      <h2>Fundamental Analysis</h2>
      <div class="news-item">{d['fundamental']}</div>
    </div>

    <div class="card" style="grid-column:1/-1">
      <h2>Social Media & Rumors</h2>
      {tweets_html}
      <div class="news-item"><strong>Hot Rumor 🔥</strong> — {d['rumor']}</div>
      <div class="news-item"><strong>Upcoming</strong> — {d['upcoming']}</div>
      <div class="sent-row">
        <span style="font-size:12px;color:#888">Fear</span>
        <div class="sent-track"><div style="width:{d['sentiment']*10}%;height:100%;background:{sent_color};border-radius:3px"></div></div>
        <span style="font-size:12px;color:#888">Greed</span>
        <span style="font-size:12px;font-weight:700;color:{sent_color};margin-right:4px">{d['sentiment']}/10 — {d['sentiment_text']}</span>
      </div>
    </div>
  </div>

  <div class="bottom-bar">
    <span style="font-size:13px;color:#888;white-space:nowrap">Today's Call</span>
    <span class="tag" style="background:{rc_bg};color:{rc_fg}">{rec}</span>
    <span style="font-size:12px;color:#666;flex:1">{d['rec_reason']}</span>
  </div>

  <div class="footer">XRP Dashboard · Auto-updated daily at 09:00 · Built with GitHub Actions + Gemini AI</div>
</div>
</body>
</html>"""


def upload_html(html, today):
    import base64
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/index.html"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    get_resp = requests.get(url, headers=headers)
    sha = get_resp.json().get("sha") if get_resp.ok else None
    content = base64.b64encode(html.encode("utf-8")).decode("utf-8")
    payload = {"message": f"XRP update {today}", "content": content}
    if sha:
        payload["sha"] = sha
    resp = requests.put(url, headers=headers, json=payload)
    if not resp.ok:
        raise Exception(f"GitHub upload error: {resp.text[:300]}")


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    }, timeout=15)
    if not resp.ok:
        raise Exception(f"Telegram error: {resp.text}")


def check_price_alert(d, today):
    change = d["change24h"]
    price  = d["price"]
    current = HOLDINGS * price
    pnl = current - INVESTED
    pnl_pct = (pnl / INVESTED) * 100

    if abs(change) >= ALERT_THRESHOLD * 100:
        direction = "🚀 PUMP" if change > 0 else "🔴 DUMP"
        msg = (
            f"{direction} ALERT — XRP {change:+.2f}% in 24h!\n\n"
            f"Price: ${price:.3f}\n"
            f"Your Portfolio: ${current:,.0f} ({pnl_pct:+.2f}%)\n"
            f"P&L: {'+' if pnl>=0 else ''}{pnl:,.0f}$\n\n"
            f"RSI: {d['rsi']} — {d['rsi_signal']}\n"
            f"Recommendation: {d['recommendation']}"
        )
        send_telegram(msg)
        print(f"Price alert sent! {change:+.2f}%")


def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    username  = GITHUB_REPO.split("/")[0]
    repo_name = GITHUB_REPO.split("/")[1]
    page_url  = f"https://{username}.github.io/{repo_name}/"

    print(f"Running XRP Agent for {today}...")
    data = get_xrp_data()
    print(f"Price: ${data['price']} | Change: {data['change24h']:+.2f}%")

    html = build_html(data, today)
    upload_html(html, today)
    print("Dashboard updated!")

    check_price_alert(data, today)

    current = HOLDINGS * data["price"]
    pnl = current - INVESTED
    pnl_pct = (pnl / INVESTED) * 100
    arrow = "📈" if pnl >= 0 else "📉"

    daily_msg = (
        f"XRP Morning Brief — {today}\n\n"
        f"Price: ${data['price']:.3f}  ({data['change24h']:+.2f}% today)\n"
        f"{arrow} Portfolio: ${current:,.0f}  ({pnl_pct:+.2f}%  {'+' if pnl>=0 else ''}{pnl:,.0f}$)\n\n"
        f"RSI: {data['rsi']} | {data['rsi_signal']}\n"
        f"Signal: {data['recommendation']}\n\n"
        f"Full Dashboard: {page_url}"
    )
    send_telegram(daily_msg)
    print("Sent to Telegram!")


if __name__ == "__main__":
    main()
