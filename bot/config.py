import os
from pathlib import Path

TOKEN = os.getenv("BOT_TOKEN")
MODEL = "u2net"                          # rembg: u2net, u2netp, sam ...
TMP_DIR = Path("/tmp/images")
TEMPLATE_PATH = Path(__file__).parent.parent / "assets" / "template.png"

# Создадим tmp-директорию, если её нет
TMP_DIR.mkdir(parents=True, exist_ok=True)
