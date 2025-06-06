
# background-replacement-bot

Телеграм-бот, который удаляет фон с присланных изображений и заменяет его на фирменный шаблон/цветовой фон. Работает локально — без сторонних API — за счёт нейросети **U²-Net** (модуль [`rembg`](https://github.com/danielgatis/rembg)). 

Пример:

![[Pasted image 20250606165902.png|700]]

## Ключевые возможности

|     | Возможность              | Детали                                                                |
| --- | ------------------------ | --------------------------------------------------------------------- |
| 🚀  | **Реальное время**       | ответ в течении 5c. на CPU (фото ≤ 2 МП)                              |
| 🧠  | **Локальная модель**     | U²-Net в ONNX, подгружается один раз и кэшируется                     |
| 🎨  | **Готовый шаблон**       | задаётся в `assets/template.png`, можно заменить на градиент/картинку |
| 🐳  | **Docker-образ <100 МБ** | быстрый деплой в облаке (Render, Railway, Fly.io)                     |
| 🔒  | **Безопасность**         | нет внешних API → фото не покидают сервер                             |
| 🛡  | **Обработка ошибок**     | валидация форматов/размера, глобальный error-handler                  |

## Системные требования

* **Python** ≥ 3.9 (проверено на 3.12)
* **pip** ≥ 22
* Для запуска без Docker — `onnxruntime` (установится автоматически через `requirements.txt`).

> 🖥 **GPU не обязателен.** При наличии NVIDIA можно заменить зависимость `onnxruntime` на `onnxruntime-gpu`, ускорив инференс.

---

## Быстрый старт

Токен моего бота - 7952373101:AAEXN-QWRxLRwmUlNkr603IAItAeHZGuGj0

### Запуск на Linux/macOS


```bash
# 1 — клон репозитория
git clone https://github.com/Radikq/background-replacement-bot.git
cd background-replacement-bot

# 2 — создание и активирование виртуального окружения
python -m venv .venv
source .venv/bin/activate

# 3 — установка зависимостей
pip install -r requirements.txt

# 4 — экспорт токена
export BOT_TOKEN="1234567890:AA..."

# 5 — запуск
python -m bot
```

### Запуск на Windows (PowerShell)

```powershell
# 1 — клонирование
git clone https://github.com/Radikq/background-replacement-bot.git
cd background-replacement-bot

# 2 — виртуальное окружение
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3 — зависимости
pip install -r requirements.txt

# 4 — переменная окружения
$env:BOT_TOKEN = "1234567890:AA..."

# 5 — запуск
python -m bot

```

Первый запрос скачает веса U²-Net (~176 МБ) в `~/.u2net/`, дальше будет работать офлайн.

## Запуск в Docker

```bash
# переменные окружения можно хранить в .env, поддерживается docker compose
export BOT_TOKEN="1234567890:AA..."

docker compose up --build
```

## Переменные окружения

|Имя|Обязательно|По умолчанию|Описание|
|---|---|---|---|
|`BOT_TOKEN`|**да**|—|API-токен бота от @BotFather|
|`MODEL`|нет|`u2net`|Название модели из `rembg` (`u2netp`, `sam`, …)|
|`TZ`|нет|`UTC`|Тайм-зона для логов Python|

Переменные читаются в `bot/config.py`.

## Структура проекта

```
background-replacement-bot/
├─ bot/                 ← тут код бота
│  ├─ handlers.py       ← логика: что делать, когда приходит фото
│  ├─ image_utils.py    ← обработка изображений: вырезка + фон
│  └─ config.py         ← пути, настройки, токен
├─ assets/              ← шаблон нового фона
│  └─ template.png
├─ requirements.txt     ← список библиотек
├─ Dockerfile           ← инструкция, как собрать образ
├─ README.md            ← описание: как запустить и как работает

```

