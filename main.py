import os
import random
import logging
import asyncio
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import requests

# === НАСТРОЙКИ ===
TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
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

# === Вебхук при первом запросе ===
@app.before_first_request
def init_webhook():
    asyncio.get_event_loop().run_until_complete(application.initialize())
    asyncio.get_event_loop().run_until_complete(application.start())

    # 🟢 Правильный URL без лишнего слэша
    webhook_target = f"https://{RENDER_URL}/{TOKEN}"
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook", params={"url": webhook_target})
    print(f"Webhook установка: {response.text}")

# === Обработка Telegram апдейтов ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.get_event_loop().create_task(application.process_update(update))
    return "OK", 200

@app.route("/")
def index():
    return "🤖 Vitamin Bot работает и ждет сообщений!"

# === Запуск Flask ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
