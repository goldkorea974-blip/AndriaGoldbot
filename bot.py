import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8165343576:AAGr_uWTBUMGCgcdahiCicHN3DehLaBOUf0"

# مهم جدًا: استخدم ID القناة الحقيقي
CHANNEL_ID = -1001234567890  # غيّره لرقم قناتك

logging.basicConfig(level=logging.INFO)

# نخزن آخر سعر (عام لكل البوت)
last_data = {"global": None}


# ===== جلب أسعار الذهب =====
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

        for item in items:
            t = item.get_text(" ", strip=True)
            parts = t.split()

            if len(parts) >= 2:
                text += f"{parts[0]} | {' '.join(parts[1:])}\n"

        return text

    except Exception as e:
        return f"❌ Error: {e}"


# ===== التحديث التلقائي =====
async def check_updates(context: ContextTypes.DEFAULT_TYPE):
    new_data = get_gold_table()
    global last_data

    if last_data["global"] != new_data:
        last_data["global"] = new_data

        msg = "📢 تحديث أسعار الذهب:\n\n" + new_data[:4000]

        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=msg
        )


# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_gold_table()

    last_data["global"] = data

    await update.message.reply_text(
        "✅ أسعار الذهب الحالية:\n\n" + data[:4000]
    )


# ===== تشغيل البوت =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # تشغيل التحديث كل دقيقة
    app.job_queue.run_repeating(
        check_updates,
        interval=60,
        first=10
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
