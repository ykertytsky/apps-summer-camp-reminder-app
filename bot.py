import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
TOKEN = "6927808593:AAFkjBYDL3iz20uK6IrBf2bPnODgQkLUq_4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я бот який буде нагадувати тобі про твої завдання.\n\n Введи /instruction для отримання інструкцій по роботі з ботом.")
async def instruction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ще нема інструкції.")

    
def main():
    
    try:
        app = Application.builder().token(TOKEN).build()
    except Exception as e:
        print(f"Помилка створення Application: {e}")
        return

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("instruction", instruction_command))

    try:
        print("Запускаємо бота...")
        app.run_polling()
    except Exception as e:
        print(f"Виникла помилка: {e}")

if __name__ == '__main__':
    main()