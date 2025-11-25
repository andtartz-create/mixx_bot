import os
import re
import json
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ ===
TOKEN = os.environ.get("BOT_TOKEN")          # токен бота
SHEET_URL = os.environ.get("SHEET_URL")      # URL Google Apps Script
PORT = int(os.environ.get("PORT", 10000))

app = Flask(__name__)


# === ПАРСЕР СМС ===
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


# === ОТПРАВКА В GOOGLE SHEETS ===
def send_to_sheet(payment):
    try:
        r = requests.post(SHEET_URL, json=payment, timeout=10)
        print("Sheet response:", r.status_code, r.text)
    except Exception as e:
        print("Error sending to sheet:", e)


# === TELEGRAM: обработка сообщений ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    payments = parse_sms(text)

    if not payments:
        await update.message.reply_text("❌ В тексте не найдено платежей.")
        return

    for p in payments:
        send_to_sheet(p)

    await update.message.reply_text(f"✅ Отправлено {len(payments)} платежей в таблицу.")


# === TELEGRAM APPLICATION (без poller) ===
application = Application.builder().token(TOKEN).updater(None).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# === WEBHOOK ===
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        print("Update error:", e)
    return "OK", 200


@app.route("/")
def home():
    return "Bot is running!"


# === ЗАПУСК НА RENDER ===
if __name__ == "__main__":
    import asyncio

    async def init_bot():
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook/{TOKEN}"
        await application.bot.set_webhook(webhook_url)
        print("Webhook set:", webhook_url)

    asyncio.get_event_loop().run_until_complete(init_bot())
    app.run(host="0.0.0.0", port=PORT)
