import os
import re
import json
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ ===
TOKEN = os.environ.get("BOT_TOKEN")  # Токен Telegram бота
SHEET_URL = os.environ.get("SHEET_URL")  # URL скрипта Google Apps Script (Web App)
PORT = int(os.environ.get("PORT", 10000))

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
        r = requests.post(SHEET_URL, json=payment, timeout=10)
        print(f"Отправлено в таблицу: {r.status_code}")
    except Exception as e:
        print(f"Ошибка отправки в таблицу: {e}")


# === ОБРАБОТКА СООБЩЕНИЙ ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text
    payments = parse_sms(text)
    if not payments:
        await update.message.reply_text("❌ Не найдено платежей в тексте.")
        return
    for p in payments:
        send_to_sheet(p)
    await update.message.reply_text(f"✅ Добавлено {len(payments)} платежей в Google Sheets.")


# === СОЗДАЁМ TELEGRAM-ПРИЛОЖЕНИЕ ===
application = Application.builder().token(TOKEN).updater(None).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# === НАСТРОЙКА WEBHOOK ===
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    """Обработка входящих апдейтов от Telegram."""
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        print(f"Ошибка обработки апдейта: {e}")
    return "OK", 200


@app.route("/")
def home():
    return "✅ Bot is running!"


# === ЗАПУСК ===
if __name__ == "__main__":
    import asyncio

    async def main():
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook/{TOKEN}"
        await application.bot.set_webhook(webhook_url)
        print(f"Webhook установлен: {webhook_url}")
        app.run(host="0.0.0.0", port=PORT)

    asyncio.run(main())
