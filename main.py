import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '7753729694:AAGZsZeqgN_E7jBSM05oYU8xqQ9QhX8AH8E'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I am your bot.')

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE, quote_text: str = None):
    if quote_text:
        await update.message.reply_text(f'Hey this is your quote for today: {quote_text}')
    else:
        await update.message.reply_text('No quote was provided.')

def make_quote_handler(quote_text):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f'Hey this is your quote for today: {quote_text}')
    return handler

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('quote', make_quote_handler("Some custom quote")))
    app.run_polling()
