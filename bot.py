import os
import asyncio
import requests
from telegram import Bot
from telegram.ext import Application, CommandHandler

API_TOKEN = os.getenv("8302361033:AAG7RSVjyeARUPbnqqXowgeaC0j9aPNz_M8")
CHAT_ID = os.getenv("5305661461")

async def start(update, context):
    await update.message.reply_text("🤖 Monitoramento iniciado com sucesso!")

async def monitorar(context):
    bot = Bot(token=API_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text="📊 Jogo em andamento... (exemplo)")

async def main():
    app = Application.builder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    job_queue = app.job_queue
    job_queue.run_repeating(monitorar, interval=60, first=10)
    await app.run_polling()

if _name_ == "_main_":
    asyncio.run(main())