<div align="center">

# 🔥 Discord Clan Bot + Google Sheets

### Умный Discord-бот для учета посещаемости, статистики игроков и управления составом клана

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge)
![Discord](https://img.shields.io/badge/Discord-Bot-5865F2?style=for-the-badge)
![Google Sheets](https://img.shields.io/badge/Google-Sheets-34A853?style=for-the-badge)
![Windows](https://img.shields.io/badge/Windows-Supported-success?style=for-the-badge)

</div>

---

## 🚀 Возможности

* ✅ Учет присутствия игроков
* ✅ Учет отсутствий с причиной
* ✅ Запись статистики по этапам
* ✅ Добавление и исключение игроков
* ✅ Автоотчеты по отсутствующим
* ✅ Работа по игровым дням
* ✅ Google Sheets как база данных
* ✅ Полная автоматизация клана

---

## 📸 Как работает система

```text
Игрок пишет команду в Discord
          ↓
Бот принимает данные
          ↓
Google Sheets обновляется
          ↓
Офицеры видят статистику
```

---

## ⚙️ Команды игроков

```text
/здесь
/немогу причина
/stat этап убийства смерти счет
```

## 🛡️ Команды администрации

```text
/add ник
/кик ник
/players
/когонет
/начатьучет
/cleartoday
/createday дата
/clearday дата
/adminhere ник
/admincant ник причина
/flush
```

---

## 📦 Быстрая установка

### 1. Установить Python

[https://www.python.org/downloads/](https://www.python.org/downloads/)

Во время установки включить:

```text
Add Python to PATH
```

### 2. Установить библиотеки

```bash
pip install discord.py gspread gspread-formatting python-dotenv google-auth
```

### 3. Структура проекта

```text
ClanBot/
├── main.py
├── .env
├── credentials.json
├── requirements.txt
└── README.md
```

---

## 🤖 Настройка Discord Bot (подробно)

1. Открыть сайт:
   [https://discord.com/developers/applications](https://discord.com/developers/applications)

2. Войти в Discord аккаунт при необходимости

3. Нажать `New Application`

4. Ввести название бота.

5. Перейти во вкладку `Bot` → `Add Bot`

6. Нажать `Reset Token`

7. Скопировать токен

8. Ниже включить:

```text
MESSAGE CONTENT INTENT
SERVER MEMBERS INTENT
```

---

## 📊 Настройка Google Таблицы (готовый шаблон)

Тебе НЕ нужно создавать таблицу вручную.

Используй готовый шаблон:

[https://docs.google.com/spreadsheets/d/1YRckeDjtTxk_e_R3WC0ZIw6xICstGHJkj3j7rY_EeQM/edit?usp=sharing](https://docs.google.com/spreadsheets/d/1YRckeDjtTxk_e_R3WC0ZIw6xICstGHJkj3j7rY_EeQM/edit?usp=sharing)

### Что сделать:

1. Открой ссылку.
2. Нажми:

```text
Файл → Создать копию
```

3. Назови таблицу как удобно.
4. Сохрани копию себе на Google Drive.

После этого у тебя будет полностью готовая таблица:

```text
Шаблон
Игроки
Формулы
Оформление
Статистика
```

### Затем вставь ссылку своей копии в `.env`

```env
GOOGLE_SHEET_URL=сюда_ссылку_твоей_копии
```

### Как получить ссылку:

1. Открой свою копию таблицы.
2. Скопируй ссылку из браузера.
3. Вставь в `.env`

---

## 🔐 Google API

Открыть [https://console.cloud.google.com/](https://console.cloud.google.com/)

Включить:

```text
Google Sheets API
Google Drive API
```

Создать Service Account и скачать JSON ключ.
Переименовать файл в:

```text
credentials.json
```

Добавить `client_email` из файла в доступ Google Таблицы как редактора.

---

## 🧩 Файл .env (что куда вставлять)

```env
DISCORD_TOKEN=сюда_токен_бота
GOOGLE_SHEET_URL=сюда_ссылку_на_твою_копию_таблицы
REPORT_CHANNEL_ID=сюда_id_канала_отчетов

PLAYERS_SHEET_NAME=Игроки
TEMPLATE_SHEET_NAME=Шаблон

TIMEZONE_OFFSET=3
COMMANDS_EPHEMERAL=true

ENABLE_MISSING_REPORT=true
REPORT_TIME=23:00

WAR_DAYS=3,4,5

FLUSH_INTERVAL_SECONDS=25

ENABLE_LATE_MARK_COLOR=true
LATE_MARK_AFTER=19:00

START_ROW=2
BLOCK_HEIGHT=4
BLOCK_END_COLUMN_INDEX=11
```

---

## ▶️ Запуск бота

```bash
python main.py
```

Если Windows пишет что python не найден:

```bash
py main.py
```

Если успешно:

```text
Бот запущен
```

---

## 🖥️ Автозапуск Windows (чтобы бот запускался сам)

1. Нажать `Win + R`
2. Ввести:

```text
shell:startup
```

3. Откроется папка автозагрузки

4. Создать файл `start_bot.bat`

```bat
cd /d C:\ClanBot
python main.py
```

---

## 🆔 Как узнать ID Discord канала

1. Discord → Настройки пользователя.
2. Дополнительно.
3. Включить `Режим разработчика`.
4. ПКМ по нужному каналу.
5. `Копировать ID`.
6. Вставить в `.env` как:

```env
REPORT_CHANNEL_ID=1234567890
```

---

## ❓ Частые ошибки

### Команды не появились

Подожди 1-5 минут.

### credentials.json not found

Файл лежит не в папке проекта.

### Spreadsheet not found

Таблица не открыта для service account.

### Ошибка 429

Увеличить:

```env
FLUSH_INTERVAL_SECONDS=40
```

---

## ❤️ Поддержка проекта

Если бот оказался полезен и хочешь поддержать автора:

<div align="center">

# 🎁 Игровой ник:

# Andrewivannik

</div>

---

<div align="center">

# ✅ Готово

После настройки бот полностью автоматизирует учет посещаемости и статистики клана.

### Удачной игры ⚔️

</div>
