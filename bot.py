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


# ================= SCRAPE (FIXED) =================
def get_prices():
    try:
        url = "https://edahabapp.com/"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.find_all("div", class_="price-item")

        data = {}

        for item in items:
            text = item.get_text(" ", strip=True)

            # تنظيف أقوى
            text = text.replace("\n", " ").strip()
            parts = text.split()

            if len(parts) >= 2:
                name = parts[0].strip()
                price = parts[1].replace(",", "").strip()

                if price.isdigit():
                    data[name] = int(price)

        return data

    except Exception as e:
        print("SCRAPE ERROR:", e)
        return {}


# ================= IMAGE =================
def create_image(new_data, old_data=None):
    img = Image.new("RGB", (800, 450), (18, 18, 28))
    draw = ImageDraw.Draw(img)

    draw.text((250, 10), "📊 GOLD MARKET LIVE", fill=(255, 215, 0))

    # خطوط
    for y in range(60, 450, 40):
        draw.line([(0, y), (800, y)], fill=(40, 40, 60))

    y = 80

    for k, v in new_data.items():

        old = old_data.get(k) if old_data else None

        if old:
            diff = v - old

            if diff > 0:
                arrow = "↑"
                color = (0, 255, 0)
            elif diff < 0:
                arrow = "↓"
                color = (255, 60, 60)
            else:
                arrow = "➖"
                color = (200, 200, 200)
        else:
            arrow = "NEW"
            color = (200, 200, 200)

        draw.text((50, y), k, fill=(255, 255, 255))
        draw.text((300, y), str(v), fill=(255, 255, 255))
        draw.text((600, y), arrow, fill=color)

        y += 40

    path = "gold.png"
    img.save(path)
    return path


# ================= MONITOR LOOP =================
async def monitor(app):
    global last_prices

    while True:
        new_data = get_prices()

        print("DEBUG DATA:", new_data)  # مهم جدًا للتأكد

        if not new_data:
            await asyncio.sleep(10)
            continue

        # 🔥 أول تشغيل: إرسال أول سعر
        if last_prices is None:
            img = create_image(new_data)

            await app.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=open(img, "rb"),
                caption="📊 أول أسعار الذهب"
            )

            last_prices = new_data
            await asyncio.sleep(10)
            continue

        # 🔥 تحديث عند التغيير
        if new_data != last_prices:
            img = create_image(new_data, last_prices)

            await app.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=open(img, "rb"),
                caption="📢 تحديث أسعار الذهب"
            )

            last_prices = new_data

        await asyncio.sleep(10)


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت شغال وبيحدث القناة تلقائيًا")


# ================= MAIN =================
async def post_init(app):
    app.create_task(monitor(app))


def main():
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))

    print("🚀 Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
