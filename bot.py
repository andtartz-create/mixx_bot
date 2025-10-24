import os
import re
import json
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters

# === НАСТРОЙКИ ===
TOKEN = os.environ.get("BOT_TOKEN")  # токен Telegram
SHEET_URL = os.environ.get("SHEET_URL")  # URL скрипта Google Apps Script (Web App)
PORT = int(os.environ.get("PORT", 10000))

bot = Bot(token=TOKEN)
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
def handle_message(update, context):
    text = update.message.text
    payments = parse_sms(text)
    if not payments:
        update.message.reply_text("❌ Не найдено платежей в тексте.")
        return
    for p in payments:
        send_to_sheet(p)
    update.message.reply_text(f"✅ Добавлено {len(payments)} платежей в Google Sheets.")


# === НАСТРОЙКА WEBHOOK ===
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    disp
