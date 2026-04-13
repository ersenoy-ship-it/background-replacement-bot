# bot/handlers.py
import os
import threading
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.error import TelegramError, BadRequest, NetworkError, TimedOut
from telegram.ext import (
    Application, ContextTypes, CommandHandler,
    MessageHandler, filters
)
from PIL import UnidentifiedImageError
from flask import Flask

from .config import TOKEN
from .image_utils import remove_bg, replace_bg

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Пришлите фото — я удалю фон и наложу фирменный шаблон.\n"
        "Файл < 8 МБ, форматы JPG/PNG."
    )


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    tg_photo = msg.photo[-1]
    if tg_photo.file_size > 8 * 1024 * 1024:  # 8 МБ
        return await msg.reply_text("Файл слишком большой (> 8 МБ).")

    file = await tg_photo.get_file()
    img_bytes = await file.download_as_bytearray()

    try:
        fg = remove_bg(img_bytes)
        result_bytes = replace_bg(fg)
        await msg.reply_photo(result_bytes, caption="Готово ✅")
    except UnidentifiedImageError:
        await msg.reply_text("Не удалось прочитать изображение. Отправьте PNG/JPG.")
    except MemoryError:
        await msg.reply_text("Изображение слишком большое для обработки. Попробуйте меньшее.")
    except Exception as e:
        logger.exception("Ошибка обработки фото")
        await msg.reply_text("⚠️ Что-то пошло не так. Попробуйте ещё раз.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled exception", exc_info=context.error)
    if update and getattr(update, "effective_chat", None):
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Произошла внутренняя ошибка. Попробуйте позднее."
            )
        except TelegramError:
            logger.error("Failed to send error message to user")


# --- ВЕБ-СЕРВЕР ДЛЯ HEALTH CHECK ---
def start_webserver():
    """Запускает минимальный Flask-сервер для health check Render."""
    web_app = Flask(__name__)
    
    @web_app.route('/')
    def health_check():
        return "Bot is running!", 200
    
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


def run_bot():
    """Запускает Telegram-бота."""
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.PHOTO, photo))
    bot_app.add_error_handler(error_handler)
    
    logger.info("Bot started")
    bot_app.run_polling(allowed_updates=["message", "edited_message"])


# --- ГЛАВНЫЙ ЗАПУСК ---
def main():
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=start_webserver, daemon=True)
    web_thread.start()
    
    # Запускаем бота в основном потоке
    run_bot()


if __name__ == "__main__":
    main()
