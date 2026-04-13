from io import BytesIO

from loguru import logger
from PIL import Image
from rembg import remove, new_session

from .config import MODEL, TEMPLATE_PATH

# Максимальный размер изображения перед обработкой
MAX_IMAGE_SIZE = (1024, 1024)  # 1024x1024 пикселей

BACKGROUND = Image.open(TEMPLATE_PATH).convert("RGBA")
SESSION = new_session("u2netp")


def resize_if_needed(image: Image.Image) -> Image.Image:
    """Уменьшает изображение, если оно превышает MAX_IMAGE_SIZE"""
    if image.width > MAX_IMAGE_SIZE[0] or image.height > MAX_IMAGE_SIZE[1]:
        logger.info(f"Resizing image from {image.size} to {MAX_IMAGE_SIZE}")
        image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
    return image


def remove_bg(img_bytes: bytes) -> Image.Image:
    """Удаляет фон и возвращает изображение RGBA."""
    logger.info("Removing background …")
    fg = Image.open(BytesIO(img_bytes)).convert("RGBA")
    fg = resize_if_needed(fg)  # ← ДОБАВЛЕНО сжатие
    result: Image.Image = remove(fg, session=SESSION)
    return result.convert("RGBA")


def replace_bg(foreground: Image.Image) -> bytes:
    """Накладывает foreground на шаблонный фон и отдаёт PNG-байты."""
    logger.info("Compositing foreground over template …")
    bg = BACKGROUND.copy().resize(foreground.size)
    composed = Image.alpha_composite(bg, foreground)
    out = BytesIO()
    composed.save(out, format="PNG")
    return out.getvalue()
