import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"  # уникальный путь для безопасности

app = Flask(__name__)

# --- Telegram bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен!")

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# --- Flask endpoint для Telegram webhook ---
@app.route(WEBHOOK_PATH, methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.create_task(application.update_queue.put(update))
    return "OK"

# --- Flask endpoint для SMS ---
@app.route("/sms", methods=["POST"])
def sms():
    data = request.get_json()
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Google Apps Script
    try:
        requests.post(WEBHOOK_URL, json=data)
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "error", "error": str(e)}, 500

# --- Устанавливаем webhook в Telegram вручную перед запуском Flask ---
def set_webhook():
    bot = Bot(BOT_TOKEN)
    url = f"{os.environ.get('RENDER_EXTERNAL_URL')}{WEBHOOK_PATH}"
    bot.delete_webhook()
    bot.set_webhook(url)
    print("Webhook установлен:", url)

if __name__ == "__main__":
    set_webhook()  # вызываем перед запуском Flask
    app.run(host="0.0.0.0", port=PORT)
