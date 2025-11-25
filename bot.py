import os
import re
import json
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio

TOKEN = os.environ.get("BOT_TOKEN")
SHEET_URL = os.environ.get("SHEET_URL")
PORT = int(os.environ.get("PORT", 10000))
HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

app = Flask(__name__)

# === PARSE SMS ===
def parse_sms(text):
    pattern = r"Umepokea TSh ([\d,]+).*?kwa (Wakala - )?([^,;]+).*?Salio.*?ni TSh ([\d,]+)"
    matches = re.findall(pattern, text)
    payments = []
    for m in matches:
        amount = m[0].replace(",", "")
        wakala = m[2].strip()
        balance = m[3].replace(",", "")
        payments.append({"amount": amount, "wakala": wakala, "balance": balance})
    return payments

# === SEND TO GOOGLE SHEETS ===
def send_to_sheet(payment):
    try:
        r = requests.post(SHEET_URL, json=payment, timeout=10)
        print("Sent to sheet:", r.status_code)
    except Exception as e:
        print("Sheet error:", e)

# === TELEGRAM BOT APP ===
application = Application.builder().token(TOKEN).updater(None).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text
    payments = parse_sms(text)
    if not payments:
        await update.message.reply_text("❌ Не найдено платежей.")
        return
    for p in payments:
        send_to_sheet(p)
    await update.message.reply_text(f"✅ Добавлено: {len(payments)}")

application.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

# === WEBHOOK ENDPOINT (SYNC!) ===
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        application.create_task(application.process_update(update))
    except Exception as e:
        print("Update error:", e)
    return "OK", 200

@app.route("/")
def home():
    return "Bot OK!"

# === START BOT & SET WEBHOOK ===
async def init_bot():
    await application.initialize()
    await application.start()

    webhook_url = f"https://{HOSTNAME}/webhook/{TOKEN}"
    await application.bot.set_webhook(webhook_url)

    print("Webhook set:", webhook_url)

# Run bot init BEFORE flask
asyncio.get_event_loop().run_until_complete(init_bot())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
