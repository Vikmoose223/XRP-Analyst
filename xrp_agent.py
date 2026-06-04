import sys, datetime, requests, os

GEMINI_API_KEY     = os.environ["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

PROMPT = """אתה סוכן ניתוח מטבעות קריפטו מקצועי המתמחה ב-XRP/Ripple.
חפש באינטרנט נתונים עדכניים וצור סקירה יומית מפורטת בעברית.

📊 *מחיר ומצב שוק*
מחיר נוכחי, שינוי 24 שעות, שינוי שבועי, נפח מסחר, מגמה כללית.

📈 *ניתוח טכני מפורט*
RSI עם ערך מדויק ומשמעות, MACD האם חיובי או שלילי, ממוצעים נעים MA20 MA50 MA200.
תמיכות: 3 רמות מחיר מדויקות.
התנגדויות: 3 רמות מחיר מדויקות.
תבנית גרף פעילה אם קיימת.

🎯 *נקודות כניסה מומלצות*
כניסה אגרסיבית: מחיר ותנאים.
כניסה שמרנית: מחיר ותנאים.
סטופ לוס מומלץ: מחיר מדויק.
יעד רווח TP1: מחיר.
יעד רווח TP2: מחיר.
יחס סיכוי סיכון: חישוב.

🔍 *ניתוח פונדמנטלי*
חדשות אחרונות מ-24 שעות, עדכוני Ripple, מצב תיק SEC, שותפויות, רגולציה.

💬 *סושיאל מדיה ושמועות*
3 עד 5 ציוצים בולטים מאנשי מפתח עם שם המשתמש והתוכן.
שמועות חמות שמסתובבות ברשת.
פרסומים ואירועים צפויים.
סנטימנט כללי ציון 1 עד 10 עם הסבר.

⚡ *המלצת מסחר*
Strong Buy או Buy או Hold או Sell או Strong Sell.
הסבר קצר של 2 עד 3 משפטים.

כתוב בעברית. ציין מספרים מדויקים. אל תמציא נתונים."""


def get_briefing(today):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": f"{PROMPT}\n\nתאריך היום: {today}"}]}],
        "tools": [{"google_search": {}}]
    }
    resp = requests.post(url, json=payload, timeout=60)
    if not resp.ok:
        raise Exception(f"Gemini error {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def send_telegram(message, today):
    header = f"📋 *סקירת XRP יומית — {today}*\n\n"
    full = header + message
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for chunk in [full[i:i+4000] for i in range(0, len(full), 4000)]:
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
           
            "disable_web_page_preview": True
        }, timeout=15)
        if not resp.ok:
            raise Exception(f"Telegram error: {resp.text}")


def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    print(f"מריץ Agent עבור {today}...")
    briefing = get_briefing(today)
    send_telegram(briefing, today)
    print("נשלח בהצלחה!")


if __name__ == "__main__":
    main()
