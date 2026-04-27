import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "PUT_YOUR_TOKEN_HERE"

# 🔴 حط ID القناة الحقيقي (مهم جدًا)
CHANNEL_ID = -1001234567890

logging.basicConfig(level=logging.INFO)

# تخزين آخر بيانات
last_data = {"global": None}


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
        print("ERROR:", e)
        return f"❌ Error: {e}"


# ===== التحديث التلقائي =====
async def check_updates(context: ContextTypes.DEFAULT_TYPE):
    print("Checking updates...")

    new_data = get_gold_table()

    global last_data

    if last_data["global"] != new_data:
        last_data["global"] = new_data

        msg = "📢 تحديث أسعار الذهب:\n\n" + new_data[:4000]

        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=msg
        )

        print("Sent to channel")


# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_gold_table()
    last_data["global"] = data

    await update.message.reply_text(
        "✅ أسعار الذهب الحالية:\n\n" + data[:4000]
    )


# ===== اختبار القناة =====
async def test_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="✅ البوت نجح في الإرسال للقناة"
    )


# ===== تشغيل البوت =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test_channel))

    # تشغيل التحديث كل دقيقة
    app.job_queue.run_repeating(
        check_updates,
        interval=60,
        first=1
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
