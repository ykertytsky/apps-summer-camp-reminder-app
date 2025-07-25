from user import *
import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import random

def load_quotes():
    result = []
    with open("quotes.txt", "r", encoding="utf-8") as file:
        for line in file:
            parts = [p.strip() for p in line.strip().split("~") if p.strip()]
            if len(parts) >= 2:
                result.append({"quote": parts[0], "author": parts[1]})
            elif len(parts) == 1:
                result.append({"quote": parts[0], "author": ""})
    return result

quotes = load_quotes()
numbers = 0

def return_one(quotes, number):
    try:
        q = quotes[number]
        return f'"{q["quote"]}" - {q["author"]}'
    except IndexError:
        return "Цитату не знайдено."

# Placeholder for TOKEN (replace with your actual bot token from @BotFather)
TOKEN = "7753729694:AAGZsZeqgN_E7jBSM05oYU8xqQ9QhX8AH8E"
users = {}  # Dictionary to store user instances with their IDs as keys

# Define conversation states for the reminder process
TASK, TIME, DEADLINE = range(3)

# Функція для обробки команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["/start",  "/info","/view_tasks"],
        ["/add_reminder", "/cancel"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Привіт! Я бот, який буде нагадувати тобі про твої завдання.\n\n"
        "Введи /info для отримання інформації по роботі з ботом.", reply_markup=reply_markup)
    user_id = update.effective_user.id
    append_user(str(user_id))
    return ReplyKeyboardMarkup(
        keyboard,  # Список кнопок
        resize_keyboard=True  # Зменшує розмір клавіатури до вмісту
    )

# Функція для обробки команди /instruction
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть /add_reminder, щоб додати нагадування.\nВведіть /view_tasks, щоб переглянути всі нагадування.\nВведіть /cancel, щоб скасувати нагадування.")

# Функція для початку додавання нагадування
async def add_reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть завдання, яке ви хочете нагадати.")
    return TASK
async def view_tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        tasks = get_all_tasks(str(user_id))
        for task in tasks:
            for i in task:
                deadline = i[1]
                await update.message.reply_text(f"Завдання: {i[0]} \nграничний час,: {deadline}")
        if not tasks:
            await update.message.reply_text("Немає нагадувань.")
    except KeyError:
        await update.message.reply_text("Помилка: користувач не знайдений. Введіть /start для початку роботи.")
# Функція для отримання завдання
async def get_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reminder_data"] = {}
    context.user_data["reminder_data"]["task"] = update.message.text
    await update.message.reply_text("Введіть час нагадування. Наприклад: 25-07-2025 15:00")
    return TIME

async def send_delayed_message(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=job.data)

# Функція для отримання часу нагадування
async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = update.message.text
    try:
        time = datetime.datetime.strptime(time_str, "%d-%m-%Y %H:%M")
        context.user_data["reminder_data"]["time"] = time
    except ValueError:
        await update.message.reply_text("Введіть коректний час. Наприклад: 25-07-2025 15:00")
        return TIME
    await update.message.reply_text("Введіть крайній термін виконання. Наприклад: 26-07-2025 15:00")
    return DEADLINE

# Функція для отримання дедлайну
async def get_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deadline_str = update.message.text
    try:
        deadline = datetime.datetime.strptime(deadline_str, "%d-%m-%Y %H:%M")
        context.user_data["reminder_data"]["deadline"] = deadline
        reminder = context.user_data.get("reminder_data", {})
        user_id = update.effective_user.id
        try:
            add_task(str(user_id),reminder["task"], reminder["time"], reminder["deadline"])
            now = datetime.datetime.now()

            # Обчислюємо час виконання завдання
            scheduled_time = reminder["time"]

            # Формуємо повідомлення
            message = f"Завдання: {reminder['task']}\nЧас виконання: {scheduled_time.strftime('%d.%m.%Y %H:%M')}" + return_one(quotes, random.randint(0, len(quotes) - 1))

            # Перевіряємо, чи час виконання завдання у майбутньому
            if scheduled_time <= now:
                await update.message.reply_text("Час має бути у майбутньому!")
                return

            # Обчислюємо затримку в секундах
            delay = (scheduled_time - now).total_seconds()

            # Плануємо відправку
            context.job_queue.run_once(send_delayed_message, delay, chat_id=update.effective_chat.id, data=message)
            
        except KeyError:
            await update.message.reply_text("Помилка: користувач не знайдений. Введіть /start для початку роботи.")
    except ValueError:
        await update.message.reply_text("Введіть коректний час. Наприклад: 26-07-2025 15:00")
        return DEADLINE
    return ConversationHandler.END

# Функція для скасування
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Запис нагадування скасовано.")
    return ConversationHandler.END

def main():
    try:
        app = Application.builder().token(TOKEN).build()
    except Exception as e:
        print(f"Помилка створення Application: {e}")
        return

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_reminder", add_reminder_command)],
        states={
            TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_task)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
            DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_deadline)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("view_tasks", view_tasks_command))

    try:
        print("Запускаємо бота...")
        app.run_polling()
    except Exception as e:
        print(f"Виникла помилка: {e}")

if __name__ == '__main__':
    main()