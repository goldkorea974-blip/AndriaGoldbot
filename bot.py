import logging
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from PIL import Image, ImageDraw

TOKEN = "PUT_YOUR_TOKEN"
CHANNEL_ID = "@AndriaGold"

logging.basicConfig(level=logging.INFO)

last_prices = None


# ========== GET PRICES ==========
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

    except:
        return {}


# ========== IMAGE ==========
def create_image(new_data, old_data=None):
    img = Image.new("RGB", (800, 450), (18, 18, 28))
    draw = ImageDraw.Draw(img)

    draw.text((250, 10), "📊 GOLD MARKET LIVE", fill=(255, 215, 0))

    y = 80

    for k, v in new_data.items():

        old = old_data.get(k) if old_data else None

        if old:
            diff = v - old
            arrow = "↑" if diff > 0 else "↓" if diff < 0 else "➖"
        else:
            arrow = "NEW"

        draw.text((50, y), k, fill=(255, 255, 255))
        draw.text((300, y), str(v), fill=(255, 255, 255))
        draw.text((600, y), arrow, fill=(0, 255, 0))

        y += 35

    path = "gold.png"
    img.save(path)
    return path


# ========== MONITOR ==========
async def monitor(app):
    global last_prices

    while True:
        new_data = get_prices()

        if not new_data:
            await asyncio.sleep(10)
            continue

        # 🔥 أول تشغيل: إرسال أول سعر فورًا
        if last_prices is None:
            img = create_image(new_data)

            await app.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=open(img, "rb"),
                caption="📊 أول تحديث لأسعار الذهب"
            )

            last_prices = new_data
            await asyncio.sleep(10)
            continue

        # 🔥 بعد كده: تحديث عند التغيير فقط
        if new_data != last_prices:
            img = create_image(new_data, last_prices)

            await app.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=open(img, "rb"),
                caption="📢 تحديث أسعار الذهب"
            )

            last_prices = new_data

        await asyncio.sleep(10)


# ========== START ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت شغال وبيحدث القناة تلقائيًا")


# ========== POST INIT ==========
async def post_init(app):
    app.create_task(monitor(app))


# ========== MAIN ==========
def main():
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))

    print("🚀 Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
