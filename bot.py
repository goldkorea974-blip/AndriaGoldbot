import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8165343576:AAGr_uWTBUMGCgcdahiCicHN3DehLaBOUf0"

logging.basicConfig(level=logging.INFO)


# ===== جلب الأسعار =====
def get_gold_table():
    try:
        url = "https://edahabapp.com/"
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, headers=headers, timeout=10)
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


# ===== أمر /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id  # 👈 أهم سطر

    await update.message.reply_text(
        "✅ أهلاً 👋\nالبوت شغال وهيبعت لك أسعار الذهب كل دقيقة"
    )

    # تشغيل job خاص بكل مستخدم
    context.job_queue.run_repeating(
        send_prices,
        interval=60,
        first=3,
        chat_id=chat_id,
        name=str(chat_id)
    )


# ===== إرسال الأسعار =====
async def send_prices(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id

    data = get_gold_table()

    await context.bot.send_message(
        chat_id=chat_id,
        text=data[:4000]
    )


# ===== تشغيل البوت =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
