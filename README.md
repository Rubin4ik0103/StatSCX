# 🔥 Discord Clan Bot + Google Sheets

!\[Python](https://img.shields.io/badge/Python-3.11+-blue)
!\[Discord](https://img.shields.io/badge/Discord-Bot-5865F2)
!\[Google Sheets](https://img.shields.io/badge/Google-Sheets-34A853)
!\[Windows](https://img.shields.io/badge/Windows-Supported-success)
!\[License](https://img.shields.io/badge/License-Private-lightgrey)

> Руководство по установке, настройке и запуску Discord-бота для учета посещаемости, статистики и управления составом клана через Google Таблицы.

\---

## 🗂 Структура проекта

```text
ClanBot/
├── main.py
├── .env
├── credentials.json
├── requirements.txt
└── README.md
```

## 🚀 Возможности проекта

✅ Автоматический учет посещаемости

✅ Google Sheets как база данных

✅ Статистика игроков по этапам

✅ Управление составом через Discord

✅ Автоотчеты по отсутствующим

✅ Работа по расписанию игровых дней

\---

## Что умеет бот

* Учет присутствия: `/здесь`
* Учет отсутствия: `/немогу причина`
* Внесение статистики: `/stat этап убийства смерти счет`
* Добавление игроков: `/add ник`
* Исключение игроков: `/кик ник`
* Список игроков: `/players`
* Кто не отметился: `/когонет`
* Принудительный запуск учета: `/начатьучет`
* Сброс дня: `/cleartoday`
* Создание дня по дате: `/createday`
* Ручные админ-отметки

\---

## 📸 Схема работы

```text
Discord Users
   ↓
Discord Bot
   ↓
Google Sheets API
   ↓
Google Таблица (учет / статистика / отчеты)
```

# 📦 1. Что потребуется

* Windows ПК / сервер
* Python 3.11+
* Discord сервер
* Google аккаунт
* Google Таблица

\---

# 🐍 2. Установка Python

Скачать Python:

https://www.python.org/downloads/

Во время установки включить:

`Add Python to PATH`

!\[окно установки Python с галочкой Add Python to PATH](img/python-install.png)

Проверка:

```bash
python --version
```

\---

# 📁 3. Создание папки проекта

Создай папку:

`C:\\ClanBot`

Внутри будут файлы:

* `main.py`
* `.env`
* `credentials.json`

!\[фото: папка проекта с файлами](img/1.png)

\---

# ⚙️ 4. Установка библиотек

Открой CMD в папке проекта:

```bash
pip install discord.py gspread gspread-formatting python-dotenv google-auth
```

\---

# 🤖 5. Создание Discord бота

Открой:

https://discord.com/developers/applications

Нажми `New Application`.

\[фото: кнопка New Application]

Вкладка **Bot** → `Add Bot`

Нажми `Reset Token` и скопируй токен.

\---

# 6\. Включение прав бота

Во вкладке **Bot** включи:

* MESSAGE CONTENT INTENT
* SERVER MEMBERS INTENT

\---

# 7\. Добавление бота на сервер

OAuth2 → URL Generator

Отметь:

* `bot`
* `applications.commands`

Права:

* Send Messages
* Use Slash Commands
* Read Message History
* Embed Links

Открой созданную ссылку и добавь бота.

\---

# 📊 8. Создание Google Таблицы

Создай новую таблицу Google Sheets.

Создай листы:

* `Шаблон`
* `Игроки`

\---

# 9\. Лист Игроки

Заполни:

|A|B|
|-|-|
|Ник|Дата вступления|
|Player1|01.04.2026|
|Player2|01.04.2026|



\---

# 10\. Лист Шаблон

Создай блок игрока в диапазоне `A2:K5`.

Пример структуры:

* A2 Дата и время
* B2 время
* C2 ник
* D2 1 этап
* E2 2 этап
* F2 3 этап
* G2 участие

Ниже строки статистики.

Справа можешь сделать топы и формулы.



\---

# 🔐 11. Создание Google API

Открой:

https://console.cloud.google.com/

Создай проект.

Далее:

API \& Services → Library

Включи:

* Google Sheets API
* Google Drive API



\---

# 12\. Service Account

API \& Services → Credentials

Create Credentials → Service Account

После создания:

Keys → Add Key → JSON

Скачай файл.

Переименуй в:

`credentials.json`

Помести в папку проекта.

\---

# 13\. Доступ таблице

Открой `credentials.json`

Найди:

`client\_email`

Скопируй адрес.

Открой таблицу → Поделиться → добавь этот email как редактора.

\---

# 🧩 14. Файл .env

Создай `.env`

```env
DISCORD\_TOKEN=токен\_бота
GOOGLE\_SHEET\_URL=https://docs.google.com/spreadsheets/d/XXXXX/edit
REPORT\_CHANNEL\_ID=1234567890
PLAYERS\_SHEET\_NAME=Игроки
TEMPLATE\_SHEET\_NAME=Шаблон
TIMEZONE\_OFFSET=3
COMMANDS\_EPHEMERAL=true
ENABLE\_MISSING\_REPORT=true
REPORT\_TIME=23:00
WAR\_DAYS=3,4,5
FLUSH\_INTERVAL\_SECONDS=25
ENABLE\_LATE\_MARK\_COLOR=true
LATE\_MARK\_AFTER=19:00
START\_ROW=2
BLOCK\_HEIGHT=4
BLOCK\_END\_COLUMN\_INDEX=11
```

\---

# 15\. main.py

Вставь код бота в файл `main.py`.

\---

# ▶️ 16. Первый запуск

```bash
python main.py
```

Если все успешно:

`Бот запущен`

\---

# 17\. Проверка работы

В Discord введи:

```text
/players
/add Test
/здесь
/немогу работа
/stat 1 5 2 900
```

\---

# 🖥️ 18. Автозапуск на Windows

Win + R

```text
shell:startup
```

Создай файл `start\_bot.bat`

```bat
cd /d C:\\ClanBot
python main.py
```

\---

# ❓ FAQ

## Команды не появились?

Подожди 1-5 минут после запуска.

## Можно ли держать бот 24/7?

Да. Лучше VPS или домашний ПК.

## Можно ли несколько кланов?

Да, отдельная таблица + отдельный .env.

## Безопасно ли хранить токен?

Да, если не выкладывать .env публично.

# 🛠️ 19. Частые ошибки

## credentials.json not found

Файл лежит не там.

## Spreadsheet not found

Не выдан доступ таблице.

## Команды не появились

Подожди 1-5 минут.

## Ошибка 429

Увеличь:

```env
FLUSH\_INTERVAL\_SECONDS=40
```

\---

# 20\. Команды игроков

* `/здесь`
* `/немогу причина`
* `/stat этап убийства смерти счет`

# Команды админов

* `/add ник`
* `/кик ник`
* `/players`
* `/когонет`
* `/начатьучет`
* `/cleartoday`
* `/createday`
* `/clearday`
* `/adminhere`
* `/admincant`
* `/flush`

\---

# ✅ Готово

Если все настроено правильно - бот полностью автоматизирует учет клана и ежедневную работу офицеров.

\---

## 💎 Рекомендации

* Держи резервную копию таблицы.
* Не передавай токен бота другим людям.
* Используй отдельный Discord канал для отчетов.
* Раз в месяц очищай старые тестовые листы.

\---

# ❤️ Удачной игры

После настройки бот будет автоматически вести учет посещаемости и статистики в Google Таблице.

Буду благодарен любым подаркам - Andrewivannik

