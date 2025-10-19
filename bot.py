import os
import json
from flask import Flask, request
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import threading

# --- Переменные из Render Secrets ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Токен бота от BotFather
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # URL Google Apps Script
PORT = int(os.environ.get("PORT", 10000))  # Render требует переменную PORT

# --- Flask app для приема POST ---
app = Flask(__name__)

@app.route("/sms", methods=["POST"])
def sms():
    data = request.get_json()
    try:
        requests.post(WEBHOOK_URL, json=data)
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "error", "error": str(e)}, 500

# --- Telegram bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен!")

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# --- Запуск Flask и Telegram одновременно ---
if __name__ == "__main__":
    threading.Thread(target=application.run_polling, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)
