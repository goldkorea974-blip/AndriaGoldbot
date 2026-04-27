import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from PIL import Image, ImageDraw

TOKEN = "8165343576:AAGr_uWTBUMGCgcdahiCicHN3DehLaBOUf0"
CHANNEL_ID = "@AndriaGold"

logging.basicConfig(level=logging.INFO)

last_prices = {}


# ================= GET PRICES =================
def get_prices():
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
        logging.error(e)
        return {}


# ================= IMAGE (PRO TRADING STYLE) =================
def create_image(new_data, old_data=None):
    width, height = 800, 500
    img = Image.new("RGB", (width, height), (15, 18, 28))
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((260, 15), "📊 GOLD MARKET LIVE", fill=(255, 215, 0))

    # Grid
    for y in range(60, height, 40):
        draw.line([(0, y), (width, y)], fill=(40, 40, 60))

    # Header box
    draw.rectangle([(20, 50), (780, 90)], outline=(255, 215, 0))

    draw.text((40, 60), "ASSET", fill="white")
    draw.text((320, 60), "PRICE", fill="white")
    draw.text((580, 60), "CHANGE", fill="white")

    y = 110

    for key, value in new_data.items():

        old = old_data.get(key) if old_data else None

        if old:
            diff = value - old
            percent = (diff / old) * 100 if old != 0 else 0

            if diff > 0:
                color = (0, 255, 0)
                arrow = f"↑ +{percent:.2f}%"
            elif diff < 0:
                color = (255, 60, 60)
                arrow = f"↓ {percent:.2f}%"
            else:
                color = (200, 200, 200)
                arrow = "➖ 0%"

        else:
            color = (200, 200, 200)
            arrow = "NEW"

        draw.text((40, y), key, fill=(255, 255, 255))
        draw.text((320, y), str(value), fill=(255, 255, 255))
        draw.text((580, y), arrow, fill=color)

        y += 40

        if y > 460:
            break

    path = "gold_market.png"
    img.save(path)
    return path


# ================= CHECK UPDATE =================
async def check_prices(context: ContextTypes.DEFAULT_TYPE):
    global last_prices

    new_data = get_prices()

    if not new_data:
        return

    # أول مرة
    if not last_prices:
        last_prices = new_data
        return

    # تغيير حصل
    if new_data != last_prices:
        img_path = create_image(new_data, last_prices)

        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=open(img_path, "rb"),
            caption="📢 تحديث جديد في أسعار الذهب"
        )

        last_prices = new_data


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت شغال وبيتابع أسعار الذهب للقناة")


# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # فحص كل 10 ثواني (لكن الإرسال عند التغيير فقط)
    app.job_queue.run_repeating(check_prices, interval=10, first=5)

    print("🚀 Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
