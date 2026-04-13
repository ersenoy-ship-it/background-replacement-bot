from telegram import Update
from telegram.constants import ParseMode
from telegram.error import TelegramError, BadRequest, NetworkError, TimedOut
from telegram.ext import (
    Application, ContextTypes, CommandHandler,
    MessageHandler, filters
)
from PIL import UnidentifiedImageError

from .config import TOKEN
from .image_utils import remove_bg, replace_bg
from loguru import logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Пришлите фото — я удалю фон и наложу фирменный шаблон.\n"
        "Файл < 8 МБ, форматы JPG/PNG."
    )


# ────────── обработка фото ──────────
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    tg_photo = msg.photo[-1]
    
    # Ограничение размера файла (уже есть, хорошо)
    if tg_photo.file_size > 8 * 1024 * 1024:  # 8 МБ
        return await msg.reply_text("Файл слишком большой (> 8 МБ).")

    # Сообщаем пользователю, что процесс пошёл
    status_msg = await msg.reply_text("⏳ Обрабатываю фото...")

    file = await tg_photo.get_file()
    img_bytes = await file.download_as_bytearray()

    try:
        # Удаляем фон
        fg = remove_bg(img_bytes)
        
        # Накладываем на шаблон
        result_bytes = replace_bg(fg)
        
        # Отправляем результат
        await msg.reply_photo(result_bytes, caption="✅ Готово!")
        await status_msg.delete()  # удаляем сообщение "Обрабатываю..."
        
    except UnidentifiedImageError:
        await status_msg.edit_text("❌ Не удалось прочитать изображение. Отправьте PNG/JPG.")
    except MemoryError:
        await status_msg.edit_text("❌ Изображение слишком большое для обработки. Попробуйте меньшее (до 2000x2000 пикселей).")
    except Exception as e:
        logger.exception("Ошибка обработки фото")
        await status_msg.edit_text("⚠️ Что-то пошло не так. Попробуйте ещё раз.")


# ────────── глобальный error handler ──────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled exception", exc_info=context.error)
    # постараемся вежливо сообщить пользователю, если чат доступен
    if update and getattr(update, "effective_chat", None):
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Произошла внутренняя ошибка. Попробуйте позднее."
            )
        except TelegramError:
            # даже сообщение не смогли отправить — лишь логируем
            logger.error("Failed to send error message to user")


# ────────── сборка приложения ──────────
def run() -> None:
    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo))

    # обработчик «всё остальное»
    app.add_error_handler(error_handler)

    logger.info("Bot started")
    app.run_polling(allowed_updates=["message", "edited_message"])
