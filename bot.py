import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8165343576:AAGr_uWTBUMGCgcdahiCicHN3DehLaBOUf0"

# قناة النشر
CHANNEL_ID = "@AndriaGold"

logging.basicConfig(level=logging.INFO)

# نخزن آخر بيانات لكل شات
last_data = {}


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


# ===== التحديثات التلقائية =====
async def check_updates(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id

    new_data = get_gold_table()
    global last_data

    # لو حصل تغيير
    if last_data.get(chat_id) != new_data:
        last_data[chat_id] = new_data

        msg = "📢 تحديث أسعار الذهب:\n\n" + new_data[:4000]

        # إرسال للمستخدم
        await context.bot.send_message(
            chat_id=chat_id,
            text=msg
        )

        # إرسال للقناة
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=msg
        )


# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    data = get_gold_table()
    last_data[chat_id] = data

    await update.message.reply_text(
        "✅ أهلاً 👋\nدي أسعار الذهب الحالية:\n\n" + data[:4000]
    )

    # حذف أي تحديث قديم
    for job in context.job_queue.get_jobs_by_name(str(chat_id)):
        job.schedule_removal()

    # تشغيل متابعة التحديث
    context.job_queue.run_repeating(
        check_updates,
        interval=60,   # كل دقيقة
        first=60,
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
