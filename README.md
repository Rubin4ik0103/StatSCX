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

- ✅ Учет присутствия игроков  
- ✅ Учет отсутствий с причиной  
- ✅ Запись статистики по этапам  
- ✅ Добавление и исключение игроков  
- ✅ Автоотчеты по отсутствующим  
- ✅ Работа по игровым дням  
- ✅ Google Sheets как база данных  
- ✅ Полная автоматизация клана  

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

https://www.python.org/downloads/

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

## 🤖 Настройка Discord Bot

1. Открыть https://discord.com/developers/applications
2. New Application
3. Bot → Add Bot
4. Reset Token
5. Включить:

```text
MESSAGE CONTENT INTENT
SERVER MEMBERS INTENT
```

---

## 📊 Настройка Google Таблицы

Создать таблицу и листы:

```text
Шаблон
Игроки
```

### Игроки

| Ник | Дата вступления |
|-----|-----------------|
| Player1 | 01.04.2026 |
| Player2 | 01.04.2026 |

### Шаблон

```text
A2:K5
```

```text
A2 Дата и время
B2 Время
C2 Ник
D2 1 этап
E2 2 этап
F2 3 этап
G2 Участие
```

---

## 🔐 Google API

Открыть https://console.cloud.google.com/

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

## 🧩 Файл .env

```env
DISCORD_TOKEN=ВАШ_ТОКЕН
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/XXXXX/edit
REPORT_CHANNEL_ID=1234567890

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

## ▶️ Запуск

```bash
python main.py
```

Если успешно:

```text
Бот запущен
```

---

## 🖥️ Автозапуск Windows

Win + R → `shell:startup`

Создать файл `start_bot.bat`

```bat
cd /d C:\ClanBot
python main.py
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

