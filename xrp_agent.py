import sys, datetime, requests, os

GEMINI_API_KEY     = os.environ["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

PROMPT = """אתה סוכן ניתוח מטבעות קריפטו מקצועי המתמחה ב-XRP/Ripple.
חפש באינטרנט נתונים עדכניים וצור סקירה יומית קצרה וממוקדת בעברית.

הסקירה לפי הסדר הבא:

📊 מחיר ומצב שוק
שורה אחת בלבד: מחיר נוכחי, שינוי 24 שעות, שינוי שבועי, מגמה.

📈 ניתוח טכני — תמציתי
RSI: ערך + משמעות בקצרה.
MACD: חיובי או שלילי + האם הייתה חצייה.
תמיכות קריטיות: 2 רמות בלבד.
התנגדויות קריטיות: 2 רמות בלבד.
תבנית פעילה אם קיימת — משפט אחד.

🎯 נקודות כניסה
כניסה: מחיר מדויק.
סטופ לוס: מחיר מדויק.
TP1: מחיר. TP2: מחיר.
יחס סיכוי/סיכון: מספר בלבד.

🔍 ניתוח פונדמנטלי — מפורט
חפש לעומק את החדשות החשובות ביותר מ-48 השעות האחרונות:
- עדכונים מ-Ripple Labs רשמיים
- מצב תיק ה-SEC וכל התפתחות משפטית
- שותפויות חדשות או הכרזות מוסדיות
- עדכוני רגולציה גלובלית שמשפיעים על XRP
- נתוני אימוץ של XRPL ו-RLUSD
כתוב פסקה מלאה על כל נושא משמעותי שמצאת.

🐦 טוויטר וחדשות רשת — עיקרי
חפש את הציוצים והפוסטים החשובים ביותר על XRP מהיום:
- ציין שם משתמש מדויק וציטוט או תקציר של הציוץ
- התמקד בחשבונות משמעותיים: Ripple, Brad Garlinghouse, David Schwartz, אנליסטים ידועים
- שמועות חמות שמסתובבות בקהילה
- פרסומים או אירועים צפויים שהקהילה מדברת עליהם
- ציון סנטימנט 1 עד 10 עם הסבר קצר

📺 גרף חי
כתוב את השורה הבאה כמות שהיא בלי שינוי:
גרף XRP/USD בזמן אמת: https://www.tradingview.com/chart/?symbol=XRPUSDT

⚡ המלצה
Strong Buy / Buy / Hold / Sell / Strong Sell — משפט הסבר אחד.

כתוב בעברית תקינה. ציין מספרים מדויקים. אל תמציא נתונים."""


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
