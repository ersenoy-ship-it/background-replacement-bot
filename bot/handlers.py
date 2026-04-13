# bot/handlers.py
import threading
from flask import Flask  # добавьте этот импорт в начало файла

# ... весь ваш существующий код (импорты, функции start, photo, error_handler, run) ...

# --- НОВЫЙ КОД ДЛЯ ВЕБ-СЕРВЕРА ---
def start_webserver():
    """Запускает минимальный Flask-сервер для health check Render."""
    app = Flask(__name__)
    
    @app.route('/')
    def health_check():
        return "Bot is running!", 200
    
    port = int(os.environ.get('PORT', 10000))
    # Важно: host='0.0.0.0', чтобы Render мог подключиться
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def run_bot():
    """Запускает Telegram-бота."""
    from .config import TOKEN
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
    app.add_error_handler(error_handler)
    
    logger.info("Bot started")
    app.run_polling(allowed_updates=["message", "edited_message"])

# --- ГЛАВНЫЙ ЗАПУСК (меняем тут) ---
def main():
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=start_webserver, daemon=True)
    web_thread.start()
    
    # Запускаем бота в основном потоке (или тоже в потоке - как удобнее)
    run_bot()

if __name__ == "__main__":
    main()
