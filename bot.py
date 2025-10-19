import os
import json
from flask import Flask, request, Response
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Параметры ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Установи в Render как переменную окружения
PORT = int(os.environ.get("PORT", "10000"))
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook/{BOT_TOKEN}"

# --- Flask ---
app = Flask(__name__)

# --- Telegram ---
application = ApplicationBuilder().token(BOT_TOKEN).build()
bot = Bot(BOT_TOKEN)

# --- Команды бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот.")

application.add_handler(CommandHandler("start", start))

# --- Webhook ---
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        application.update_queue.put(update)
    except Exception as e:
        print(f"Ошибка обработки update: {e}")
    return Response("OK", status=200)

# --- Настройка вебхука при старте ---
@app.before_first_request
def set_webhook():
    import asyncio
    async def main():
        await bot.delete_webhook()
        await bot.set_webhook(WEBHOOK_URL)
        print(f"Webhook установлен: {WEBHOOK_URL}")
    asyncio.run(main())

# --- Запуск Flask ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
