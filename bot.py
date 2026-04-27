import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "PUT_YOUR_TOKEN"

logging.basicConfig(level=logging.INFO)

# نخزن آخر سعر لكل مستخدم
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


# ===== إرسال تحديث لو فيه تغيير =====
async def check_updates(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id

    new_data = get_gold_table()

    global last_data

    # لو اتغير → ابعت
    if last_data.get(chat_id) != new_data:
        last_data[chat_id] = new_data

        await context.bot.send_message(
            chat_id=chat_id,
            text="📢 تحديث جديد:\n\n" + new_data[:4000]
        )


# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # أول رسالة فوراً
    data = get_gold_table()
    last_data[chat_id] = data

    await update.message.reply_text(
        "✅ أهلاً 👋\nدي أسعار الذهب الحالية:\n\n" + data[:4000]
    )

    # شيل أي job قديم لنفس المستخدم
    for job in context.job_queue.get_jobs_by_name(str(chat_id)):
        job.schedule_removal()

    # شغل متابعة التغيير فقط
    context.job_queue.run_repeating(
        check_updates,
        interval=60,
        first=60,  # يبدأ يراقب بعد دقيقة
        chat_id=chat_id,
        name=str(chat_id)
    )


# ===== تشغيل البوت =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
