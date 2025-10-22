import os
import random
import logging
import asyncio
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import requests

# === НАСТРОЙКИ ===
TOKEN = os.getenv("BOT_TOKEN", "8260202137:AAHc9MvaZAVlFfQwgHUsYi6z6ps2_Ekx1NE")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "vitamin-bot-mwr4.onrender.com")
PORT = int(os.environ.get("PORT", 5000))

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO)

# === СООБЩЕНИЯ ===
CUTE_MESSAGES = [
    "💖 Принцесса, не забудь про витамины!",
    "✨ Звёздочка, пора принять витаминки!",
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
    msg1 = random.choice(CUTE_MESSAGES)
    msg2 = random.choice(SUCCESS_MESSAGES)
    await update.message.reply_text(msg1)
    await asyncio.sleep(2)
    await update.message.reply_text(msg2)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Статистика пока не подключена, но ты уже молодец!")

# === Flask + Telegram ===
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Regex("💊 Напомнить сейчас"), remind))
application.add_handler(MessageHandler(filters.Regex("📊 Статистика"), stats))

# === Webhook ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Получение апдейтов от Telegram"""
    update = Update.de_json(request.get_json(force=True), application.bot)

    async def process():
        if not application.running:
            await application.initialize()
        await application.process_update(update)

    asyncio.run(process())
    return "OK", 200


@app.route("/")
def index():
    return "🤖 Vitamin Bot is alive!"


if __name__ == "__main__":
    # Устанавливаем webhook при запуске
    webhook_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://{RENDER_URL}/{TOKEN}"
    print("Setting webhook:", requests.get(webhook_url).text)

    app.run(host="0.0.0.0", port=PORT)
