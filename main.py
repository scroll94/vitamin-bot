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

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "8260202137:AAHc9MvaZAVlFfQwgHUsYi6z6ps2_Ekx1NE")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "vitamin-bot-mwr4.onrender.com")  # без https://
WEBHOOK_URL = f"https://{RENDER_URL}/{BOT_TOKEN}"
PORT = int(os.environ.get("PORT", 5000))
DATA_FILE = "user_data.json"

# ========== ЛОГИ ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== Flask ==========
app = Flask(__name__)

# ========== Telegram Application ==========
application = Application.builder().token(BOT_TOKEN).build()

# ========= Вспомогательные функции для данных ==========
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

# ========= Тексты и клавиатуры ==========
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

# ========= Обработчики (вся твоя логика, сохранена и адаптирована) ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    if user_id not in user_data:
        user_data[user_id] = {'vitamin_count': 0, 'reminders': [], 'total_reminders': 0}
        save_user_data(user_data)

    welcome_text = """
💖 *Привет, моя прекрасная!* 🎀

Я твой персональный напоминатель о витаминах! 

*Что я умею:*
• 💊 Напоминать принимать витамины
• ⏰ Устанавливать ежедневные напоминания
• 📊 Показывать твою статистику
• 🎀 Поддерживать милыми сообщениями

Выбери что хочешь сделать 👇
"""
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode='Markdown')

async def send_reminder_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = random.choice(CUTE_MESSAGES)
    await update.message.reply_text(f"💖 *Напоминание!*\n\n{message}", reply_markup=get_confirm_keyboard(), parse_mode='Markdown')

async def setup_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏰ *Выбери время для ежедневного напоминания:*\n\n"
        "Я буду напоминать тебе каждый день в выбранное время! 💖",
        reply_markup=get_time_keyboard(),
        parse_mode='Markdown'
    )

async def handle_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    time_map = {
        "🕘 7:30": "07:30",
        "🕛 12:00": "12:00",
        "🕒 15:00": "15:00",
        "🕕 18:00": "18:00",
        "🕘 21:00": "21:00"
    }
    if text in time_map:
        selected_time = time_map[text]
        await save_reminder(update, context, user_id, selected_time)
    elif text == "⏰ Другое время":
        await update.message.reply_text(
            "💖 *Введи время в формате ЧЧ:MM*\n\nНапример: 8:00 или 14:30",
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_time'] = True
    elif text == "📋 Главное меню":
        await update.message.reply_text("Возвращаемся в главное меню 💖", reply_markup=get_main_keyboard())

async def save_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str, time_str: str):
    user_data = load_user_data()
    if 'reminders' not in user_data[user_id]:
        user_data[user_id]['reminders'] = []
    user_data[user_id]['reminders'].append({
        'time': time_str,
        'active': True,
        'created': datetime.now().isoformat()
    })
    user_data[user_id]['total_reminders'] = user_data[user_id].get('total_reminders', 0) + 1
    save_user_data(user_data)
    success_text = random.choice([
        f"🎉 *Отлично!* Теперь я буду напоминать тебе каждый день в *{time_str}*! 💖",
        f"✨ *Запомнила!* Буду присылать напоминания в *{time_str}* каждый день! 🎀",
        f"💕 *Супер!* Напоминания установлены на *{time_str}*! Теперь я о тебе позабочусь! 🌸"
    ])
    await update.message.reply_text(success_text, reply_markup=get_main_keyboard(), parse_mode='Markdown')

async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_stats = load_user_data().get(user_id, {})
    vitamin_count = user_stats.get('vitamin_count', 0)
    total_reminders = user_stats.get('total_reminders', 0)
    active_reminders = len([r for r in user_stats.get('reminders', []) if r.get('active', True)])
    if vitamin_count == 0:
        comment = "💖 Начни заботиться о себе сегодня!"
    elif vitamin_count < 5:
        comment = "🎀 Ты на правильном пути! Продолжай в том же духе!"
    elif vitamin_count < 10:
        comment = "✨ Уже хороший результат! Горжусь тобой!"
    else:
        comment = "🌟 Вау! Ты настоящая молодец! 💫"
    text = f"""
📊 *Твоя статистика заботы о себе* 💖

💊 *Приемов витаминов:* {vitamin_count} раз
⏰ *Активных напоминаний:* {active_reminders}
📅 *Всего установлено:* {total_reminders} напоминаний

{comment}
"""
    await update.message.reply_text(text, reply_markup=get_main_keyboard(), parse_mode='Markdown')

async def show_my_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    reminders = load_user_data().get(user_id, {}).get('reminders', [])
    active_reminders = [r for r in reminders if r.get('active', True)]
    if not active_reminders:
        text = "📝 *У тебя пока нет активных напоминаний*\n\nНажми '⏰ Установить напоминание' чтобы создать первое! 💖"
    else:
        text = "📝 *Твои напоминания:*\n\n"
        for reminder in active_reminders:
            text += f"• 🕐 {reminder['time']}\n"
        text += f"\n🎀 Всего напоминаний: {len(active_reminders)}\nЯ буду напоминать тебе каждый день! 💕"
    await update.message.reply_text(text, reply_markup=get_main_keyboard(), parse_mode='Markdown')

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    if text == "✅ Приняла витамины":
        user_data = load_user_data()
        user_data[user_id]['vitamin_count'] = user_data[user_id].get('vitamin_count', 0) + 1
        save_user_data(user_data)
        success_message = random.choice(SUCCESS_MESSAGES)
        await update.message.reply_text(success_message, reply_markup=get_main_keyboard(), parse_mode='Markdown')
    elif text == "🕐 Напомнить позже":
        await update.message.reply_text("💖 Хорошо, напомню через 2 часа! 🕐", reply_markup=get_main_keyboard())
        # Напоминаем через 2 часа
        context.job_queue.run_once(callback=send_delayed_reminder, when=7200, chat_id=user_id, data=user_id)
    elif text == "📋 Главное меню":
        await update.message.reply_text("Главное меню 💖", reply_markup=get_main_keyboard())

async def send_delayed_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.data
    try:
        message = random.choice(CUTE_MESSAGES)
        await context.bot.send_message(chat_id=user_id, text=f"💖 *Напоминаю снова!*\n\n{message}", reply_markup=get_confirm_keyboard(), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в отложенном напоминании: {e}")

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        if context.user_data.get('waiting_for_time'):
            try:
                time_obj = datetime.strptime(text, "%H:%M")
                time_str = time_obj.strftime("%H:%M")
                user_id = str(update.effective_user.id)
                await save_reminder(update, context, user_id, time_str)
                context.user_data['waiting_for_time'] = False
                return
            except ValueError:
                await update.message.reply_text("❌ Неверный формат! Введи время как ЧЧ:MM\nНапример: 8:00 или 14:30")
                return
        if text == "💊 Напомнить сейчас":
            await send_reminder_now(update, context)
        elif text == "⏰ Установить напоминание":
            await setup_reminder(update, context)
        elif text == "📊 Моя статистика":
            await show_statistics(update, context)
        elif text == "📝 Мои напоминания":
            await show_my_reminders(update, context)
        elif text in ["✅ Приняла витамины", "🕐 Напомнить позже"]:
            await handle_confirmation(update, context)
        elif text in ["🕘 7:30", "🕛 12:00", "🕒 15:00", "🕕 18:00", "🕘 21:00", "⏰ Другое время"]:
            await handle_time_selection(update, context)
        else:
            await update.message.reply_text("💖 Выбери действие из меню 👇", reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("💔 Что-то пошло не так...", reply_markup=get_main_keyboard())

# ========= РЕГИСТРАЦИЯ ХЕНДЛЕРОВ ==========
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))

# ========= WEBHOOK (Flask endpoint) ==========
@app.route("/", methods=["GET"])
def index():
    return "✅ Vitamin Bot is alive!", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        # безопасно ставим задачу в уже работающий loop приложения
        application.create_task(application.process_update(update))
        return "ok", 200
    except Exception as e:
        logger.exception("Ошибка в webhook:")
        return "error", 500

# ========= Фоновый запуск application (loop в отдельном потоке) ==========
async def _start_application():
    """Инициализируем и стартуем application (job queue и т.д.) и установим webhook в Telegram."""
    await application.initialize()
    await application.start()
    # Устанавливаем webhook на Telegram (через бот)
    try:
        await application.bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"Webhook установлен: {WEBHOOK_URL}")
    except Exception as e:
        logger.exception("Ошибка установки webhook:")

def _run_async_loop_forever():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(_start_application())
    loop.run_forever()

# ========= Главная точка входа ==========
if __name__ == "__main__":
    # Запускаем background event loop в отдельном треде (чтобы job_queue работал)
    t = threading.Thread(target=_run_async_loop_forever, daemon=True)
    t.start()
    logger.info("Запущен бекграунд цикл приложения (telegram application).")

    # Запускаем Flask (синхронный) — он принимает webhook POST и кладёт update в loop приложения
    app.run(host="0.0.0.0", port=PORT)

