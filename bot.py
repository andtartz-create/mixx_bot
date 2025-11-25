import os
import re
import json
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ ===
TOKEN = os.environ.get("BOT_TOKEN")
SHEET_URL = os.environ.get("SHEET_URL")
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
        payments.append({"amount": amount, "wakala": wakala
