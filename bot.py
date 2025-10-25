import os
import re
import json
import requests
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
application = Application.builder().token(TOKEN).updater(None).build()

# === НАСТРОЙКИ ===
TOKEN = os.environ.get("BOT_TOKEN")
SHEET_URL = os.environ.get("SHEET_URL")
PORT = int(os.environ.get("PORT", 10000))
HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

app = Flask(__name__)

# === ФУНКЦИЯ ПАРСИНГА SMS ===
def parse_sms(text):
    pattern = r"Umepokea TSh ([\d,]+).*?kwa (Wakala - )?([^,;]+).*?Salio.*?ni TSh ([\d,]+)"
    matches = re.findall(pattern, text)
    payments = []
    for m in matches:
        amount = m[0].replace(",", "")
        wakala = m[2].strip()
        balance = m[3].replace(",", "")
        payments.append({
            "amount": amount,
            "wakala": wakala,
            "balance": balance
        })
    return payments


# === ОТПРАВКА ДАННЫХ В GOOGLE SHEETS ===
def send_to_sheet(payment):
    try:
        requests.post(SHEET_URL, json=payment, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки в таблицу: {e}")


# === ОБРАБОТКА СООБЩЕНИЙ ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    payments = parse_sms(text)
    if not payments:
        await update.message.reply_text("❌ Не найдено платежей в тексте.")
        return
    for p in payments:
        send_to_sheet(p)
    await update.message.reply_text(f"✅ Добавлено {len(payments)} платежей в Google Sheets.")


# === СОЗДАНИЕ APPLICATION (без updater/polling) ===
application = Application.builder().token(TOKEN).updater(None).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# === WEBHOOK ОБРАБОТЧИК ===
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok", 200


# === УСТАНОВКА WEBHOOK ПЕРЕД ЗАПУСКОМ ===
@app.before_serving
async def setup_webhook():
    if HOSTNAME:
        url = f"https://{HOSTNAME}/webhook/{TOKEN}"
        await application.bot.delete_webhook()
        await application.bot.set_webhook(url)
        print(f"✅ Webhook установлен: {url}")
    else:
        print("⚠️ Переменная RENDER_EXTERNAL_HOSTNAME не найдена.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

