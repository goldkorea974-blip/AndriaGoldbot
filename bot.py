import asyncio
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8165343576:AAGr_uWTBUMGCgcdahiCicHN3DehLaBOUf0"
CHANNEL_ID = "@AndriaGold"

logging.basicConfig(level=logging.INFO)

last_data = None


# ===== SCRAPE =====
def get_gold_table():
    try:
        url = "https://edahabapp.com/"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.find_all("div", class_="price-item")

        data = {}

        for item in items:
            text = item.get_text(" ", strip=True)
            parts = text.split()

            if len(parts) >= 2:
                name = parts[0]
                price = parts[1].replace(",", "")

                if price.isdigit():
                    data[name] = int(price)

        return data

    except Exception as e:
        print("ERROR:", e)
        return {}


# ===== LOOP =====
async def monitor(app):
    global last_data

    while True:
        new_data = get_gold_table()

        print("DEBUG:", new_data)

        # أول مرة
        if last_data is None:
            await app.bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"📊 أول أسعار الذهب\n\n{new_data}"
            )
            last_data = new_data

        # تحديث
        elif new_data != last_data:
            await app.bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"📢 تحديث أسعار الذهب\n\n{new_data}"
            )
            last_data = new_data

        await asyncio.sleep(60)


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت شغال")


# ===== POST INIT =====
async def post_init(app):
    app.create_task(monitor(app))


# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
