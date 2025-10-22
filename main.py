import os
import random
import logging
import asyncio
import requests
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === НАСТРОЙКИ ===
TOKEN = os.getenv("BOT_TOKEN", "8260202137:AAHc9MvaZAVlFfQwgHUsYi6z6ps2_Ekx1NE")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "vitamin-bot-mwr4.onrender.com")
PORT = int(os.environ.get("PORT", 5000))

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
    text = random.choice(CUTE
