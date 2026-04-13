# start.py
import os
import sys
import threading

# Добавляем папку с ботом в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.handlers import main

if __name__ == "__main__":
    main()
