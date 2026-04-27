import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "PUT_YOUR_TOKEN_HERE"
CHANNEL_ID = -1001234567890  # غيّره

logging.basicConfig(level=logging.INFO)

last_data = {"global": None}


def get_gold_table():
    try:
        url = "https://edahabapp.com/"
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, headers=headers, timeout=10)
        print("STATUS:", r.status_code)  # debug

        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("div", class_="price-item")

        if not items:
            print("⚠️ No items found - HTML changed")

        text = "📊 أسعار الذهب اليوم\n\n"

        for item in items:
            t = item.get_text(" ", strip=True)
            text += t + "\n"

        return text

    except Exception as e:
        print("ERROR:", e)
        return f"❌ Error: {e}"


async def check_updates(context: ContextTypes.DEFAULT_TYPE):
    print("Checking updates...")

    new_data = get_gold_table()

    global last_data

    if last_data["global"] != new_data:
        last_data["global"] = new_data

        print("Sending to channel...")

        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="📢 تحديث:\n\n" + new_data[:4000]
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_gold_table()
    last_data["global"] = data

    await update.message.reply_text(
        "✅ شغال\n\n" + data[:4000]
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # مهم: تشغيل job بشكل صريح
    job_queue = app.job_queue
    job_queue.run_repeating(check_updates, interval=60, first=10)

    print("BOT RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
