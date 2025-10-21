import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import json
import os
import random
from flask import Flask, request

# === НАСТРОЙКИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "8260202137:AAHc9MvaZAVlFfQwgHUsYi6z6ps2_Ekx1NE")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://vitamin-bot-mwr4.onrender.com")
DATA_FILE = "user_data.json"
PORT = int(os.environ.get("PORT", 5000))

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === ФУНКЦИИ ДАННЫХ ===
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === СООБЩЕНИЯ ===
CUTE_MESSAGES = [
    "💖 Моя прекрасная принцесса, не забудь про витамины! 🎀",
    "✨ Звездочка моя, пора принять витаминки! 💫",
    "🎀 Котик мой милый, выпей витамины для здоровья! 🐱",
    "💕 Любимая, твое здоровье - мой приоритет! Прими витамины! 🌸",
]
SUCCESS_MESSAGES = [
    "🎉 Умничка! Так держать! 💪",
    "💖 Моя самая ответственная девочка! 🥰",
    "✨ Ты просто молодец! Заботишься о себе! 🌸",
    "🎀 Вот это я понимаю - дисциплина! Горжусь тобой! 💕",
]

# === КНОПКИ ===
def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ["💊 Напомнить сейчас", "⏰ Установить напоминание"],
        ["📊 Моя статистика", "📝 Мои напоминания"]
    ], resize_keyboard=True)

def get_time_keyboard():
    return ReplyKeyboardMarkup([
        ["🕘 7:30", "🕛 12:00", "🕒 15:00"],
        ["🕕 18:00", "🕘 21:00", "⏰ Другое время"],
        ["📋 Главное меню"]
    ], resize_keyboard=True)

def get_confirm_keyboard():
    return ReplyKeyboardMarkup([
        ["✅ Приняла витамины", "🕐 Напомнить позже"],
        ["📋 Главное меню"]
    ], resize_keyboard=True)

# === ОБРАБОТЧИКИ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    if user_id not in user_data:
        user_data[user_id] = {'vitamin_count': 0, 'reminders': [], 'total_reminders': 0}
        save_user_data(user_data)

    text = "💖 Привет! Я твой бот-напоминатель о витаминах 🎀"
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

async def send_reminder_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(CUTE_MESSAGES)
    await update.message.reply_text(f"💖 *Напоминание!*\n\n{msg}", reply_markup=get_confirm_keyboard(), parse_mode='Markdown')

async def setup_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏰ Выбери время для ежедневного напоминания:", reply_markup=get_time_keyboard())

async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_user_data().get(user_id, {})
    count = user_data.get("vitamin_count", 0)
    text = f"📊 Ты уже приняла витамины {count} раз 💖"
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "💊 Напомнить сейчас":
        await send_reminder_now(update, context)
    elif text == "⏰ Установить напоминание":
        await setup_reminder(update, context)
    elif text == "📊 Моя статистика":
        await show_statistics(update, context)
    else:
        await update.message.reply_text("💖 Выбери действие из меню 👇", reply_markup=get_main_keyboard())

# === СОЗДАЕМ БОТ ===
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))

# === FLASK ===
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Vitamin Bot работает!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.create_task(application.process_update(update))
    return "ok", 200

async def set_webhook():
    await application.bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    app.run(host="0.0.0.0", port=PORT)
