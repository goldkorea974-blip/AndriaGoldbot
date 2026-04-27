import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8165343576:AAGr_uWTBUMGCgcdahiCicHN3DehLaBOUf0"
CHAT_ID = 940590742

last_prices = ""

def get_prices():
    url = "https://edahabapp.com/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.find_all("div", class_="price-item")
    result = ""

    for item in items:
        result += item.get_text(strip=True) + "\n"

    return result

async def check_prices(context: ContextTypes.DEFAULT_TYPE):
    global last_prices

    new_prices = get_prices()

    if new_prices != last_prices:
        last_prices = new_prices

        await context.bot.send_message(
            chat_id=CHAT_ID,
            text="📢 تحديث أسعار الذهب:\n\n" + new_prices[:4000]
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت شغال وهيبعت التحديثات تلقائيًا")

# تشغيل الـ job مرة واحدة
async def post_init(app):
    app.job_queue.run_repeating(check_prices, interval=60, first=5)

app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
