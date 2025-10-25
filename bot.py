import os
import re
import json
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ ===
TOKEN = os.environ.get("BOT_TOKEN")  # токен Telegram
SHEET_URL = os.environ.get("SHEET_URL")  # Google Apps Script Web App URL
PORT = int(os.environ.get("PORT", 10000))
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")  # Render автоматически задаёт этот URL

app = Flask(__name__)

# === ПАРСИНГ SMS ===
def parse_sms(text: str):
    pattern = r"Umepokea TSh ([\d,]+).*?kwa (Wakala - )?([^,;]+).*?Salio.*?ni TSh ([\d,]+)"
    matches = re.findall(pattern, text)
    payments = []
    for m in matches:
        payments.append({
            "amount": m[0].replace(",", ""),
            "wakala": m[2].strip(),
            "balance": m[3].replace(",", "")
        })
    return payments


# === ОТПРАВКА В GOOGLE SHEETS ===
def send_to_sheet(payment: dict):
    try:
        requests.post(SHEET_URL, json=payment, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки в таблицу: {e}")


# === ОБРАБОТЧИК СООБЩЕНИЙ ===
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


# === СОЗДАЁМ TELEGRAM APPLICATION ===
application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# === WEBHOOK ===
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200


# === УСТАНОВКА WEBHOOK ===
@app.before_first_request
def setup_webhook():
    if RENDER_URL:
        webhook_url = f"{RENDER_URL}/webhook/{TOKEN}"
        try:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/setWebhook",
                data={"url": webhook_url},
                timeout=10
            )
            print(f"✅ Webhook установлен: {webhook_url}")
        except Exception as e:
            print(f"❌ Ошибка установки вебхука: {e}")
    else:
        print("⚠️ Переменная RENDER_EXTERNAL_URL не установлена — Render ещё не предоставил URL.")


# === ЗАПУСК FLASK ===
if __name__ == "__main__":
    print("🚀 Бот запущен и готов к приёму обновлений!")
    app.run(host="0.0.0.0", port=PORT)
