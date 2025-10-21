import logging
import os
import requests
import os

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = f"https://vitamin-bot-mwr4.onrender.com/{TOKEN}"

# Установим вебхук при запуске
set_webhook = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
print(set_webhook.text)

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime
import random
from flask import Flask, request

# === НАСТРОЙКИ ===
TOKEN = "8260202137:AAHc9MvaZAVlFfQwgHUsYi6z6ps2_Ekx1NE"  # 🔹 вставь сюда токен от бота
PORT = int(os.environ.get("PORT", 5000))  # Render сам выдаёт порт

# === СООБЩЕНИЯ ===
CUTE_MESSAGES = [
    "💖 Принцесса, не забудь про витамины!",
    "✨ Звездочка, пора принять витаминки!",
    "🎀 Котик мой, пора заботиться о себе! 💊",
    "💕 Любимая, не забудь выпить витамины! 🌸",
]

SUCCESS_MESSAGES = [
    "🎉 Умничка! Так держать! 💪",
    "💖 Самая ответственная девочка! 🥰",
    "✨ Молодец! Заботишься о себе! 🌸",
    "🎀 Вот это дисциплина! 💕",
]

# === КНОПКИ ===
def main_keyboard():
    return ReplyKeyboardMarkup(
        [["💊 Напомнить сейчас", "📊 Статистика"]],
        resize_keyboard=True
    )

# === ОБРАБОТЧИКИ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💖 Привет, моя милая! Я твой бот-напоминатель о витаминах 🎀",
        reply_markup=main_keyboard()
    )

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = random.choice(CUTE_MESSAGES)
    await update.message.reply_text(
        text,
        reply_markup=main_keyboard()
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Ты — самая заботливая! Продолжай в том же духе 💖",
        reply_markup=main_keyboard()
    )

# === ЗАПУСК БОТА ===
app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Vitamin Bot работает!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.process_update(update)
    return 'ok', 200

async def run_bot():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("💊"), remind))
    application.add_handler(MessageHandler(filters.Regex("📊"), stats))

    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=f"https://{RENDER_URL}/{TOKEN}")

# Создаём приложение
application = Application.builder().token(TOKEN).build()

# Запуск Flask и Telegram вместе
if __name__ == '__main__':
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "localhost")
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    app.run(host='0.0.0.0', port=PORT)

