import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8165343576:AAGr_uWTBUMGCgcdahiCicHN3DehLaBOUf0"
CHANNEL_ID = "@AndriaGold"

logging.basicConfig(level=logging.INFO)

last_data = None


# ===== جلب الأسعار =====
def get_gold_table():
    try:
        url = "https://edahabapp.com/"
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("div", class_="price-item")

        text = "📊 أسعار الذهب اليوم\n\n"
        text += "العيار | السعر\n"
        text += "-----------------\n"

        data = {}

        for item in items:
            t = item.get_text(" ", strip=True)
            parts = t.split()

            if len(parts) >= 2:
                name = parts[0]
                price = parts[1].replace(",", "")

                if price.isdigit():
                    data[name] = int(price)
                    text += f"{name} | {price}\n"

        return text, data

    except Exception as e:
        return f"❌ Error: {e}", {}


# ===== متابعة التحديث =====
async def check_updates(context: ContextTypes.DEFAULT_TYPE):
    global last_data

    new_text, new_data = get_gold_table()

    if not new_data:
        return

    # أول مرة
    if last_data is None:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="📊 أول أسعار الذهب في القناة\n\n" + new_text[:4000]
        )
        last_data = new_data
        return

    # لو فيه تغيير
    if new_data != last_data:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="📢 تحديث أسعار الذهب\n\n" + new_text[:4000]
        )
        last_data = new_data


# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, data = get_gold_table()

    await update.message.reply_text(
        "✅ أهلاً 👋\nدي أسعار الذهب الحالية:\n\n" + text[:4000]
    )

    # إرسال للقناة أول مرة
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="📊 مستخدم جديد فتح البوت\n\n" + text[:4000]
    )


# ===== تشغيل البوت =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # تشغيل التحديث كل دقيقة
    app.job_queue.run_repeating(check_updates, interval=60, first=5)

    print("🚀 Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
