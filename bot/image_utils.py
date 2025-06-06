from io import BytesIO

from loguru import logger
from PIL import Image
from rembg import remove, new_session

from .config import MODEL, TEMPLATE_PATH

BACKGROUND = Image.open(TEMPLATE_PATH).convert("RGBA")
SESSION = new_session(MODEL)


def remove_bg(img_bytes: bytes) -> Image.Image:
    """Удаляет фон и возвращает изображение RGBA."""
    logger.info("Removing background …")
    fg = Image.open(BytesIO(img_bytes)).convert("RGBA")
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
