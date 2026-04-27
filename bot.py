import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ========== LOGGING ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ========== CONFIG ==========
TOKEN = "8165343576:AAGr_uWTBUMGCgcdahiCicHN3DehLaBOUf0"
CHAT_ID = 940590742

last_prices = None


# ========== GET PRICES ==========
def get_gold_table():
    try:
        url = "https://edahabapp.com/"
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("div", class_="price-item")

        if not items:
            return "⚠️ لا توجد بيانات حالياً"

        table = "📊 أسعار الذهب اليوم\n\n"
        table += "العيار | السعر\n"
        table += "------------------\n"

        for item in items:
            text = item.get_text(" ", strip=True)

            parts = text.split()

            if len(parts) >= 2:
                name = parts[0]
                price = " ".join(parts[1:])
                table += f"{name} | {price}\n"
            else:
                table += f"{text}\n"

        return table

    except Exception as e:
        logging.error(f"Error fetching prices: {e}")
        return f"❌ خطأ في جلب البيانات: {e}"


# ========== JOB ==========
async def check_prices(context: ContextTypes.DEFAULT_TYPE):
    global last_prices

    new_data = get_gold_table()

    if new_data != last_prices:
        last_prices = new_data

        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=new_data[:4000]
        )


# ========== START COMMAND ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت شغال وبيحدث أسعار الذهب تلقائيًا")


# ========== POST INIT ==========
async def post_init(app):
    app.job_queue.run_repeating(check_prices, interval=60, first=5)


# ========== MAIN ==========
def main():
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))

    logging.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
