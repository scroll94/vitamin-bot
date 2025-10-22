import os
import json
import random
import logging
import threading
import asyncio
from datetime import datetime
from flask import Flask, request
import requests

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ====== НАСТРОЙКИ ======
BOT_TOKEN = os.getenv("BOT_TOKEN", "8260202137:AAHc9MvaZAVlFfQwgHUsYi6z6ps2_Ekx1NE")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "vitamin-bot-mwr4.onrender.com")  # без https://
WEBHOOK_URL = f"https://{RENDER_URL}/{BOT_TOKEN}"
PORT = int(os.environ.get("PORT", 5000))
DATA_FILE = "user_data.json"

# ====== ЛОГИ ======
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====== Flask ======
app = Flask(__name__)

# ====== Telegram Application ======
application = Application.builder().token(BOT_TOKEN).build()

# ====== Работа с файлами ======
def load_user_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_user_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== Сообщения ======
CUTE_MESSAGES = [
    "💖 Моя прекрасная принцесса, не забудь про витамины! 🎀",
    "✨ Звездочка моя, пора принять витаминки! 💫",
    "🎀 Котик мой милый, выпей витамины для здоровья! 🐱",
    "💕 Любимая, твое здоровье - мой приоритет! Прими витамины! 🌸",
    "🌺 Прелесть моя, не забудь про витаминки! 🎀",
    "🐇 Зайка моя, пора принимать витамины! 💊",
    "🌟 Сокровище мое, не забудь о здоровье! Прими витамины! 💖"
]

SUCCESS_MESSAGES = [
    "🎉 Умничка! Так держать! 💪",
    "💖 Моя самая ответственная девочка! 🥰",
    "✨ Ты просто молодец! Заботишься о себе! 🌸",
    "🎀 Вот это я понимаю - дисциплина! Горжусь тобой! 💕",
    "🐱 Котик мой умница! Продолжай в том же духе! 💫"
]

# ====== Клавиатуры ======
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

# ====== Хендлеры ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    if user_id not in user_data:
        user_data[user_id] = {'vitamin_count': 0, 'reminders': [], 'total_reminders': 0}
        save_user_data(user_data)

    text = (
        "💖 *Привет, моя прекрасная!* 🎀\n\n"
        "Я твой персональный напоминатель о витаминах!\n\n"
        "Выбери действие ниже 👇"
    )
    await update.message.reply_text(text, reply_markup=get_main_keyboard(), parse_mode='Markdown')

async def send_reminder_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(CUTE_MESSAGES)
    await update.message.reply_text(f"💖 *Напоминание!*\n\n{msg}", reply_markup=get_confirm_keyboard(), parse_mode='Markdown')

async def setup_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏰ *Выбери время для напоминания:*",
        reply_markup=get_time_keyboard(),
        parse_mode='Markdown'
    )

async def save_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str, time_str: str):
    user_data = load_user_data()
    if 'reminders' not in user_data[user_id]:
        user_data[user_id]['reminders'] = []
    user_data[user_id]['reminders'].append({'time': time_str, 'active': True})
    user_data[user_id]['total_reminders'] = user_data[user_id].get('total_reminders', 0) + 1
    save_user_data(user_data)
    await update.message.reply_text(
        f"🎀 Запомнила! Буду напоминать тебе каждый день в *{time_str}*! 💖",
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    if text == "💊 Напомнить сейчас":
        await send_reminder_now(update, context)
    elif text == "⏰ Установить напоминание":
        await setup_reminder(update, context)
    elif text in ["🕘 7:30", "🕛 12:00", "🕒 15:00", "🕕 18:00", "🕘 21:00"]:
        await save_reminder(update, context, user_id, text.split(" ")[1])
    else:
        await update.message.reply_text("Выбери действие из меню 👇", reply_markup=get_main_keyboard())

# ====== Регистрация ======
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))

# ====== Flask Routes ======
@app.route("/", methods=["GET"])
def index():
    return "✅ Vitamin Bot is alive!", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        # Отправляем задачу в фоновый event loop (а не в Flask-поток)
        asyncio.run_coroutine_threadsafe(application.process_update(update), asyncio.get_event_loop())
        return "ok", 200
    except Exception as e:
        logger.exception("Ошибка в webhook:")
        return "error", 500

# ====== Асинхронный запуск Telegram ======
async def _start_application():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"Webhook установлен: {WEBHOOK_URL}")

def _run_async_loop_forever():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(_start_application())
    loop.run_forever()

# ====== Главный вход ======
if __name__ == "__main__":
    threading.Thread(target=_run_async_loop_forever, daemon=True).start()
    logger.info("Запущен Telegram application loop.")
    app.run(host="0.0.0.0", port=PORT)
