import re
import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import requests

# Настройки логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Токен телеграм-бота (вставь свой!)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# URL твоего Google Apps Script (скрипта приёма данных)
GOOGLE_APPS_SCRIPT_URL = os.getenv("GOOGLE_APPS_SCRIPT_URL")

# Регулярные выражения для извлечения данных из SMS
pattern = re.compile(
    r"Umepokea TSh\s*([\d,]+).*?kutoka kwa (Wakala - |)([A-Z0-9\s]+).*?Salio.*?TSh\s*([\d,]+).*?Kumbukumbu.*?(\d+)",
    re.DOTALL
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    matches = pattern.findall(text)

    if not matches:
        await update.message.reply_text("❌ Не удалось распознать ни одного платежа.")
        return

    results = []
    for amount, wakala_prefix, sender, balance, ref in matches:
        amount = amount.replace(",", "")
        balance = balance.replace(",", "")
        wakala = sender.strip()
        results.append((amount, wakala, balance, ref))

        # Отправляем в Google Script
        try:
            requests.post(GOOGLE_APPS_SCRIPT_URL, data={
                "amount": amount,
                "wakala": wakala,
                "balance": balance,
                "ref": ref
            })
        except Exception as e:
            logging.error(f"Ошибка при отправке в Google: {e}")

    msg = "\n".join(
        [f"💰 {a} от {w}\nБаланс: {b}\nRef: {r}" for a, w, b, r in results]
    )
    await update.message.reply_text(f"✅ Обработано {len(results)} платеж(ей):\n\n{msg}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
