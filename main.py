import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Replace 'YOUR_TOKEN' with your actual bot token
TOKEN = '7753729694:AAGZsZeqgN_E7jBSM05oYU8xqQ9QhX8AH8E'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I am your bot.')

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    await update.message.reply_text(f"Привіт, твоя цитата на сьогодні: {data["quote"]} - {data["author"]}")

from functools import partial

if __name__ == '__main__':
    data = {"quote": "Цитата",
         "author": "Андрій"}
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('quote', partial(quote, data = data)))
    app.run_polling()
