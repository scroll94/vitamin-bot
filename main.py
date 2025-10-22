import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import os

# === НАСТРОЙКА ЛОГОВ ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === СОЗДАЁМ FLASK ===
app = Flask(__name__)

# === ТОКЕН БОТА ===
TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")

# === СОЗДАЁМ TELEGRAM APPLICATION ===
application = Application.builder().token(TOKEN).build()


# === КОМАНДЫ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я работаю через Flask webhook 😎")


application.add_handler(CommandHandler("start", start))


# === ВЕБХУК ДЛЯ TELEGRAM ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Получаем обновления от Telegram и передаём в application"""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))  # <-- Исправлено!
    except Exception as e:
        logger.error(f"Ошибка при обработке обновления: {e}")
    return "ok", 200


# === ГЛАВНАЯ СТРАНИЦА ===
@app.route("/")
def home():
    return "Бот запущен успешно!"


# === ЗАПУСК FLASK ===
if __name__ == "__main__":
    # Устанавливаем webhook при старте
    WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    asyncio.run(application.bot.set_webhook(url=WEBHOOK_URL))

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
