import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8165343576:AAGr_uWTBUMGCgcdahiCicHN3DehLaBOUf0"

logging.basicConfig(level=logging.INFO)

# نخزن آخر بيانات لكل مستخدم
last_data = {}


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

        for item in items:
            t = item.get_text(" ", strip=True)
            parts = t.split()

            if len(parts) >= 2:
                text += f"{parts[0]} | {' '.join(parts[1:])}\n"

        return text

    except Exception as e:
        return f"❌ Error: {e}"


# ===== إرسال الأسعار =====
async def send_prices(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id

    new_data = get_gold_table()

    global last_data

    # إرسال فقط لو تغيرت البيانات
    if last_data.get(chat_id) != new_data:
        last_data[chat_id] = new_data

        await context.bot.send_message(
            chat_id=chat_id,
            text=new_data[:4000]
        )


# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    await update.message.reply_text(
        "✅ أهلاً 👋\nالبوت شغال وهيبعت لك أسعار الذهب عند التغيير"
    )

    # منع تكرار الـ job لنفس المستخدم
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    # تشغيل job خاص بكل مستخدم
    context.job_queue.run_repeating(
        send_prices,
        interval=60,
        first=3,
        chat_id=chat_id,
        name=str(chat_id)
    )


# ===== تشغيل البوت =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
