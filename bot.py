import os
import json
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Секретный токен от @BotFather
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
PORT = int(os.environ.get("PORT", 10000))

# URL вашей Google Apps Script (для записи в Google Таблицу)
GOOGLE_SCRIPT_URL = os.environ.get("GOOGLE_SCRIPT_URL")  

# --- FLASK ---
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Бот работает! ✅", 200

@app.route(WEBHOOK_PATH, methods=["POST"])
def telegram_webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    asyncio.run(application.update_queue.put(update))
    return "OK", 200

@app.route("/sms", methods=["POST"])
def sms_post():
    """Принимаем POST от Tasker/смс и отправляем в Google Таблицу"""
    try:
        data = request.get_json(force=True)
        # POST в Google Apps Script
        import requests
        requests.post(GOOGLE_SCRIPT_URL, json=data)
        return {"status": "success"}, 200
    except Exception as e:
        return {"status": "error", "error": str(e)}, 500

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Вы написали: {update.message.text}")

# --- ИНИЦИАЛИЗАЦИЯ БОТА ---
bot = Bot(BOT_TOKEN)
application = ApplicationBuilder().bot(bot).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- УСТАНОВКА WEBHOOK ---
def set_webhook():
    url = f"{os.environ.get('RENDER_EXTERNAL_URL')}{WEBHOOK_PATH}"
    asyncio.run(bot.delete_webhook())
    asyncio.run(bot.set_webhook(url))
    print("Webhook установлен:", url)

set_webhook()

# --- ЗАПУСК FLASK ---
if __na
