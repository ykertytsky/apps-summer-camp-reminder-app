from user import User
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

"""
Function: start
Description: Handles the /start command to initialize a user session and display a welcome message with a custom keyboard.
Parameters:
    - update (Update): Object containing information about the incoming update (e.g., message).
    - context (ContextTypes.DEFAULT_TYPE): Context object providing bot functionality and data.
Returns: None
Side Effects: Adds a new User instance to the 'users' dictionary and sends a welcome message.
"""
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["/start", "/add_reminder", "/view_tasks"],
        ["/info", "/cancel"]
    ]
    await update.message.reply_text("Привіт! Я бот, який буде нагадувати тобі про твої завдання.\n\n"
        "Введи /info для отримання інформації по роботі з ботом.")
    user_id = update.effective_user.id
    users[user_id] = User(user_id)

"""
Function: info_command
Description: Handles the /info command to provide instructions on how to use the bot.
Parameters:
    - update (Update): Object containing information about the incoming update.
    - context (ContextTypes.DEFAULT_TYPE): Context object for bot operations.
Returns: None
Side Effects: Sends a message with usage instructions.
"""
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть /add_reminder, щоб додати нагадування.\nВведіть /view_tasks, щоб переглянути всі нагадування.\nВведіть /cancel, щоб скасувати нагадування.")

"""
Function: add_reminder_command
Description: Initiates the reminder creation process by prompting the user to enter a task.
Parameters:
    - update (Update): Object containing the incoming update.
    - context (ContextTypes.DEFAULT_TYPE): Context for bot operations.
Returns: TASK (int) - The next conversation state.
Side Effects: Sends a prompt message to the user.
"""
async def add_reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть завдання, яке ви хочете нагадати.")
    return TASK

"""
Function: view_tasks_command
Description: Displays all tasks for the current user when the /view_tasks command is issued.
Parameters:
    - update (Update): Object containing the incoming update.
    - context (ContextTypes.DEFAULT_TYPE): Context for bot operations.
Returns: None
Side Effects: Sends messages listing all tasks or an error message if no tasks exist.
"""
async def view_tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in users:
        tasks = users[user_id].get_all_tasks()
        for task in tasks:
            for i in task:
                deadline = i[1].strftime("%d.%m.%Y %H:%M")
                await update.message.reply_text(f"Завдання: {i[0]} \nграничний час,: {deadline}")
        if not tasks:
            await update.message.reply_text("Немає нагадувань.")
    else:
        await update.message.reply_text("Помилка: користувач не знайдений. Введіть /start для початку роботи.")

"""
Function: get_task
Description: Collects the task description from the user during the reminder creation process.
Parameters:
    - update (Update): Object containing the incoming update.
    - context (ContextTypes.DEFAULT_TYPE): Context for storing user data.
Returns: TIME (int) - The next conversation state.
Side Effects: Stores the task in user_data and sends a prompt for the reminder time.
"""
async def get_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reminder_data"] = {}
    context.user_data["reminder_data"]["task"] = update.message.text
    await update.message.reply_text("Введіть час нагадування. Наприклад: 25-07-2025 15:00")
    return TIME

"""
Function: send_delayed_message
Description: Sends a delayed message to the user at the scheduled time using the job queue.
Parameters:
    - context (ContextTypes.DEFAULT_TYPE): Context object containing job details.
Returns: None
Side Effects: Sends a message to the chat specified in the job.
"""
async def send_delayed_message(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=job.data)

"""
Function: get_time
Description: Collects the reminder time from the user and validates its format.
Parameters:
    - update (Update): Object containing the incoming update.
    - context (ContextTypes.DEFAULT_TYPE): Context for storing user data.
Returns: TIME (int) if invalid, DEADLINE (int) if valid - The next conversation state.
Side Effects: Stores the time in user_data and sends a prompt for the deadline.
"""
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

"""
Function: get_deadline
Description: Collects the deadline from the user, schedules the reminder, and stores the task.
Parameters:
    - update (Update): Object containing the incoming update.
    - context (ContextTypes.DEFAULT_TYPE): Context for storing user data and job queue.
Returns: DEADLINE (int) if invalid, ConversationHandler.END if valid - The next conversation state.
Side Effects: Stores the task in the user's task list, schedules a delayed message, and sends a confirmation.
"""
async def get_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global numbers
    deadline_str = update.message.text
    try:
        deadline = datetime.datetime.strptime(deadline_str, "%d-%m-%Y %H:%M")
        context.user_data["reminder_data"]["deadline"] = deadline
        reminder = context.user_data.get("reminder_data", {})
        user_id = update.effective_user.id
        if user_id in users:
            users[user_id].add_task(reminder["task"], reminder["time"], reminder["deadline"])
            await update.message.reply_text("Нагадування додано!")
            now = datetime.datetime.now()
            scheduled_time = reminder["time"]
            # Формуємо повідомлення з цитатою
            quote_msg = return_one(quotes, numbers)
            numbers += 1
            message = f"Завдання: {reminder['task']}\nЧас виконання: {scheduled_time.strftime('%d.%m.%Y %H:%M')}\n\n{quote_msg}"
            if scheduled_time <= now:
                await update.message.reply_text("Час має бути у майбутньому!")
                return
            delay = (scheduled_time - now).total_seconds()
            context.job_queue.run_once(send_delayed_message, delay, chat_id=update.effective_chat.id, data=message)
        else:
            await update.message.reply_text("Помилка: користувач не знайдений. Введіть /start для початку роботи.")
    except ValueError:
        await update.message.reply_text("Введіть коректний час. Наприклад: 26-07-2025 15:00")
        return DEADLINE
    return ConversationHandler.END

"""
Function: cancel
Description: Handles the /cancel command to terminate the reminder creation process.
Parameters:
    - update (Update): Object containing the incoming update.
    - context (ContextTypes.DEFAULT_TYPE): Context for bot operations.
Returns: ConversationHandler.END (int) - Ends the conversation.
Side Effects: Sends a cancellation message.
"""
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Запис нагадування скасовано.")
    return ConversationHandler.END


"""
Function: main
Description: The main function to set up and run the Telegram bot application.
Returns: None
Side Effects: Initializes the bot, sets up handlers, and starts polling for updates.
"""
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