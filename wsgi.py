# wsgi.py
from flask import Flask
import threading
import os

# Импортируем вашу основную функцию для запуска бота
# Предполагается, что она лежит в bot/handlers.py и называется `main`
from bot.handlers import main as start_bot

# Создаём Flask-приложение для health check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

# Запускаем бота в отдельном фоновом потоке
bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()

# Переменная для Render, чтобы он знал, как запускать приложение
# Gunicorn будет искать именно `app`
application = app
