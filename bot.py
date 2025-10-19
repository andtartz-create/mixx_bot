import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import re
import os

# URL вашего Google Apps Script (Web App)
GSHEET_URL = "https://script.google.com/macros/s/AKfycbwE27fepOcfQVNeRY8ptzTDm1nLEAnQQ9gNbgfMnvCwtlOz1HVUWnqKo37qBzfK59sv9A/exec"

# Функция для отправки данных в таблицу
def send_to_sheet(amount, wakala, balance):
    payload = {
        "amount": amount,
        "wakala": wakala,
        "balance": balance
    }
    try:
        response = requests.post(GSHEET_URL, json=payload)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Функция обработки сообщений Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # Простейший парсер: ищем числа для amount и balance, и текст для wakala
    amount_match = re.search(r"TSh\s?([\d,]+)", text)
    balance_match = re.search(r"Salio lako jipya ni TSh\s?([\d,]+)", text)
    wakala_match = re.search(r"(?<=umepokea TSh [\d,]+ kutoka kwa )[\w\s]+", text)

    amount = amount_match.group(1).replace(",", "") if amount_match else ""
    balance = balance_match.group(1).replace(",", "") if balance_match else ""
    wakala = wakala_match.group(0) if wakala_match else ""

    # Отправляем данные в таблицу
    result = send_to_sheet(amount, wakala, balance)

    # Ответ пользователю в Telegram
    await update.message.reply_text(f"Данные отправлены: {result}")

# Основная функция запуска бота
def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # токен бота в переменной окружения
    app = ApplicationBuilder().token(TOKEN).build()

    # Вся входящая переписка
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен...")
    app.run_polling()  # Работает без Background Worker, через поллинг

if __name__ == "__main__":
    main()
