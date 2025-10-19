import requests
from telegram.ext import Updater, MessageHandler, Filters
import re
import logging

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = "8423825538:AAGVIvQDDRLsSM10AacjaV5YJnJds-xn4Ms"  # <-- вставь свой токен
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwE27fepOcfQVNeRY8ptzTDm1nLEAnQQ9gNbgfMnvCwtlOz1HVUWnqKo37qBzfK59sv9A/exec"  # <-- твой URL скрипта

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# === ОБРАБОТКА СООБЩЕНИЙ ===
def handle_message(update, context):
    text = update.message.text
    user = update.message.from_user
    logger.info(f"Получено сообщение от @{user.username}: {text[:60]}...")

    if not text:
        return

    try:
        r = requests.post(GOOGLE_SCRIPT_URL, data=text.encode('utf-8'))
        if r.status_code == 200:
            update.message.reply_text("✅ Отправлено в Google Sheet.")
        else:
            update.message.reply_text(f"⚠️ Ошибка {r.status_code}: {r.text}")
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")
        logger.error(e)

# === ЗАПУСК БОТА ===
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    logger.info("🤖 Бот запущен...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
