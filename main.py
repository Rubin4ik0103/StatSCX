import os
import asyncio
from datetime import datetime, timezone, timedelta

import discord
from discord import app_commands
from discord.ext import tasks
import gspread
from gspread_formatting import CellFormat, Color, format_cell_range
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
REPORT_CHANNEL_ID = int(os.getenv("REPORT_CHANNEL_ID", "0"))

PLAYERS_SHEET_NAME = os.getenv("PLAYERS_SHEET_NAME", "Игроки")
TEMPLATE_SHEET_NAME = os.getenv("TEMPLATE_SHEET_NAME", "Шаблон")

TIMEZONE_OFFSET = int(os.getenv("TIMEZONE_OFFSET", "3"))
TZ = timezone(timedelta(hours=TIMEZONE_OFFSET))

COMMANDS_EPHEMERAL = os.getenv("COMMANDS_EPHEMERAL", "true").lower() == "true"

ENABLE_MISSING_REPORT = os.getenv("ENABLE_MISSING_REPORT", "true").lower() == "true"
REPORT_TIME = os.getenv("REPORT_TIME", "23:00")

WAR_DAYS = [
    int(x.strip())
    for x in os.getenv("WAR_DAYS", "3,4,5").split(",")
    if x.strip()
]

FLUSH_INTERVAL_SECONDS = int(os.getenv("FLUSH_INTERVAL_SECONDS", "25"))

ENABLE_LATE_MARK_COLOR = os.getenv("ENABLE_LATE_MARK_COLOR", "true").lower() == "true"
LATE_MARK_AFTER = os.getenv("LATE_MARK_AFTER", "19:00")

START_ROW = int(os.getenv("START_ROW", "2"))
BLOCK_HEIGHT = int(os.getenv("BLOCK_HEIGHT", "4"))
BLOCK_END_COLUMN_INDEX = int(os.getenv("BLOCK_END_COLUMN_INDEX", "11"))

gc = gspread.service_account(filename="credentials.json")
spreadsheet = gc.open_by_url(GOOGLE_SHEET_URL)

try:
    players_sheet = spreadsheet.worksheet(PLAYERS_SHEET_NAME)
except gspread.WorksheetNotFound:
    players_sheet = spreadsheet.add_worksheet(title=PLAYERS_SHEET_NAME, rows=200, cols=2)
    players_sheet.update(values=[["Ник", "Дата вступления"]], range_name="A1:B1")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

write_queue = []
queue_lock = asyncio.Lock()

light_red_format = CellFormat(backgroundColor=Color(1, 0.8, 0.8))


def now_dt():
    return datetime.now(TZ)


def today_sheet_name():
    return now_dt().strftime("%Y-%m-%d")


def today_display():
    return now_dt().strftime("%d.%m.%Y")


def current_time():
    return now_dt().strftime("%H:%M")


def normalize_nick(name: str) -> str:
    return str(name).split("(")[0].strip()


def parse_time(value: str):
    h, m = value.split(":")
    return int(h), int(m)


def is_after_time(now: datetime, value: str) -> bool:
    h, m = parse_time(value)
    return (now.hour, now.minute) >= (h, m)


def is_war_day() -> bool:
    return now_dt().weekday() in WAR_DAYS


def date_to_sheet_name(date_text: str) -> str:
    parsed = datetime.strptime(date_text.strip(), "%d.%m.%Y")
    return parsed.strftime("%Y-%m-%d")


def get_players():
    rows = players_sheet.get_all_values()
    result = []

    for row in rows[1:]:
        if row and row[0].strip():
            result.append(normalize_nick(row[0]))

    return result


def get_template_sheet():
    return spreadsheet.worksheet(TEMPLATE_SHEET_NAME)


def today_sheet_exists() -> bool:
    try:
        spreadsheet.worksheet(today_sheet_name())
        return True
    except gspread.WorksheetNotFound:
        return False


def can_track_today() -> bool:
    return is_war_day() or today_sheet_exists()


def copy_block(sheet, target_start_row: int):
    source_start = START_ROW - 1
    source_end = START_ROW + BLOCK_HEIGHT - 1

    target_start = target_start_row - 1
    target_end = target_start_row + BLOCK_HEIGHT - 1

    body = {
        "requests": [
            {
                "copyPaste": {
                    "source": {
                        "sheetId": sheet.id,
                        "startRowIndex": source_start,
                        "endRowIndex": source_end,
                        "startColumnIndex": 0,
                        "endColumnIndex": BLOCK_END_COLUMN_INDEX
                    },
                    "destination": {
                        "sheetId": sheet.id,
                        "startRowIndex": target_start,
                        "endRowIndex": target_end,
                        "startColumnIndex": 0,
                        "endColumnIndex": BLOCK_END_COLUMN_INDEX
                    },
                    "pasteType": "PASTE_NORMAL",
                    "pasteOrientation": "NORMAL"
                }
            }
        ]
    }

    spreadsheet.batch_update(body)


def prepare_day_sheet(sheet):
    players = get_players()

    if not players:
        return

    sheet.batch_clear([f"A{START_ROW + BLOCK_HEIGHT}:K500"])

    updates = []

    for index, nick in enumerate(players):
        start_row = START_ROW + index * BLOCK_HEIGHT

        if index > 0:
            copy_block(sheet, start_row)

        updates.append({
            "range": f"C{start_row}",
            "values": [[nick]]
        })

    sheet.batch_update(updates)


def create_day_from_template(sheet_name: str, recreate: bool = False):
    try:
        existing = spreadsheet.worksheet(sheet_name)

        if not recreate:
            return existing

        spreadsheet.del_worksheet(existing)
    except gspread.WorksheetNotFound:
        pass

    template = get_template_sheet()

    new_sheet = spreadsheet.duplicate_sheet(
        source_sheet_id=template.id,
        new_sheet_name=sheet_name
    )

    prepare_day_sheet(new_sheet)

    return new_sheet


def get_or_create_today_sheet():
    return create_day_from_template(today_sheet_name(), recreate=False)


def get_or_create_sheet_by_date(date_text: str):
    return create_day_from_template(date_to_sheet_name(date_text), recreate=False)


def recreate_sheet_by_date(date_text: str):
    return create_day_from_template(date_to_sheet_name(date_text), recreate=True)


def recreate_today_sheet():
    return create_day_from_template(today_sheet_name(), recreate=True)


def get_today_sheet_for_write():
    if not can_track_today():
        raise Exception("Сегодня учет не ведется. Используй /начатьучет, если нужно начать учет вне дней КВ.")

    return get_or_create_today_sheet()


def find_player_block(sheet, nick: str):
    rows = sheet.get_all_values()
    clean_nick = normalize_nick(nick)

    for i in range(START_ROW - 1, len(rows), BLOCK_HEIGHT):
        row = rows[i]

        if len(row) >= 3 and normalize_nick(row[2]) == clean_nick:
            return i + 1

    return None


def find_free_block(sheet):
    rows = sheet.get_all_values()

    for start_row in range(START_ROW, 500, BLOCK_HEIGHT):
        row_index = start_row - 1

        if row_index >= len(rows):
            return start_row

        row = rows[row_index]
        nick_cell = row[2] if len(row) >= 3 else ""

        if not str(nick_cell).strip():
            return start_row

    raise Exception("Не найден свободный блок")


def ensure_player_block(sheet, nick: str):
    start_row = find_player_block(sheet, nick)

    if start_row:
        return start_row

    start_row = find_free_block(sheet)
    copy_block(sheet, start_row)
    sheet.update(values=[[normalize_nick(nick)]], range_name=f"C{start_row}")

    return start_row


def remove_player_block_from_sheet(sheet, nick: str):
    start_row = find_player_block(sheet, nick)

    if not start_row:
        return False

    rows = sheet.get_all_values()
    filled_blocks = []

    for row_num in range(START_ROW, len(rows) + 1, BLOCK_HEIGHT):
        row = rows[row_num - 1] if row_num - 1 < len(rows) else []

        if len(row) >= 3 and str(row[2]).strip():
            filled_blocks.append(row_num)

    if not filled_blocks:
        return False

    last_block_start = filled_blocks[-1]
    current = start_row

    while current + BLOCK_HEIGHT <= last_block_start:
        copy_from = current + BLOCK_HEIGHT

        body = {
            "requests": [
                {
                    "copyPaste": {
                        "source": {
                            "sheetId": sheet.id,
                            "startRowIndex": copy_from - 1,
                            "endRowIndex": copy_from + BLOCK_HEIGHT - 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": BLOCK_END_COLUMN_INDEX
                        },
                        "destination": {
                            "sheetId": sheet.id,
                            "startRowIndex": current - 1,
                            "endRowIndex": current + BLOCK_HEIGHT - 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": BLOCK_END_COLUMN_INDEX
                        },
                        "pasteType": "PASTE_NORMAL",
                        "pasteOrientation": "NORMAL"
                    }
                }
            ]
        }

        spreadsheet.batch_update(body)
        current += BLOCK_HEIGHT

    sheet.batch_clear([f"A{last_block_start}:K{last_block_start + BLOCK_HEIGHT - 1}"])
    return True


async def queue_write(action: dict):
    async with queue_lock:
        write_queue.append(action)


async def flush_writes():
    async with queue_lock:
        if not write_queue:
            return 0

        actions = write_queue.copy()
        write_queue.clear()

    try:
        sheet = get_today_sheet_for_write()
        count = 0
        updates = []
        late_absences = []

        for action in actions:
            nick = normalize_nick(action["nick"])
            start_row = ensure_player_block(sheet, nick)

            if action["type"] == "mark":
                status = action["status"]
                reason = action["reason"]
                mark_time = action["time"]
                participation = "✅" if status == "был" else "❌"

                updates.extend([
                    {"range": f"B{start_row}", "values": [[mark_time]]},
                    {"range": f"B{start_row + 2}", "values": [[status]]},
                    {"range": f"B{start_row + 3}", "values": [[reason]]},
                    {"range": f"G{start_row + 1}", "values": [[participation]]},
                ])

                if (
                    ENABLE_LATE_MARK_COLOR
                    and status == "не был"
                    and is_after_time(now_dt(), LATE_MARK_AFTER)
                ):
                    late_absences.append(f"B{start_row}")

            elif action["type"] == "stat":
                round_number = action["round"]
                kills = action["kills"]
                deaths = action["deaths"]
                score = action["score"]

                target_col = chr(64 + 3 + round_number)

                updates.extend([
                    {"range": f"{target_col}{start_row + 1}", "values": [[kills]]},
                    {"range": f"{target_col}{start_row + 2}", "values": [[deaths]]},
                    {"range": f"{target_col}{start_row + 3}", "values": [[score]]},
                    {"range": f"B{start_row + 2}", "values": [["был"]]},
                    {"range": f"G{start_row + 1}", "values": [["✅"]]},
                ])

            count += 1

        if updates:
            sheet.batch_update(updates)

        for cell_range in late_absences:
            format_cell_range(sheet, cell_range, light_red_format)

        return count

    except Exception:
        async with queue_lock:
            write_queue[0:0] = actions
        raise


def get_missing_today():
    sheet = get_today_sheet_for_write()
    rows = sheet.get_all_values()

    missing = []

    for i in range(START_ROW - 1, len(rows), BLOCK_HEIGHT):
        row = rows[i]

        if len(row) < 3:
            continue

        nick = row[2]

        if not nick:
            continue

        participation = ""

        if i + 1 < len(rows):
            row2 = rows[i + 1]
            if len(row2) >= 7:
                participation = row2[6]

        if not participation:
            missing.append(nick)

    return missing


def add_player_to_sheet(nick: str):
    clean_nick = normalize_nick(nick)

    if clean_nick in get_players():
        return False

    players_sheet.append_row([clean_nick, today_display()])

    if today_sheet_exists():
        sheet = get_or_create_today_sheet()
        ensure_player_block(sheet, clean_nick)

    return True


def kick_player_from_sheet(nick: str):
    clean_nick = normalize_nick(nick)
    rows = players_sheet.get_all_values()

    removed_from_players = False

    for index, row in enumerate(rows[1:], start=2):
        if row and normalize_nick(row[0]) == clean_nick:
            players_sheet.delete_rows(index)
            removed_from_players = True
            break

    if today_sheet_exists():
        sheet = get_or_create_today_sheet()
        remove_player_block_from_sheet(sheet, clean_nick)

    return removed_from_players


def build_missing_report():
    missing = get_missing_today()

    if not missing:
        return "✅ Сегодня все игроки отметились."

    return "❌ Сегодня не отметились:\n" + "\n".join(f"- {nick}" for nick in missing)


@bot.event
async def on_ready():
    await tree.sync()

    if is_war_day():
        get_or_create_today_sheet()

    if not queue_flusher.is_running():
        queue_flusher.start()

    if ENABLE_MISSING_REPORT and not daily_report.is_running():
        daily_report.start()

    print(f"Бот запущен: {bot.user}")


@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        message = "❌ У тебя нет прав для этой команды."
    else:
        message = f"❌ Ошибка команды: {error}"

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


@tree.command(name="здесь", description="Отметиться как присутствующий")
async def here(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    if not can_track_today():
        await interaction.followup.send(
            "❌ Сегодня учет не ведется. Админ может включить его командой /начатьучет.",
            ephemeral=True
        )
        return

    await queue_write({
        "type": "mark",
        "nick": interaction.user.display_name,
        "status": "был",
        "reason": "-",
        "time": current_time()
    })

    await interaction.followup.send("✅ Отметка принята.", ephemeral=COMMANDS_EPHEMERAL)


@tree.command(name="немогу", description="Отметить отсутствие")
@app_commands.describe(reason="Причина отсутствия")
async def cant(interaction: discord.Interaction, reason: str):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    if not can_track_today():
        await interaction.followup.send(
            "❌ Сегодня учет не ведется. Админ может включить его командой /начатьучет.",
            ephemeral=True
        )
        return

    await queue_write({
        "type": "mark",
        "nick": interaction.user.display_name,
        "status": "не был",
        "reason": reason,
        "time": current_time()
    })

    await interaction.followup.send(f"✅ Отсутствие принято: {reason}", ephemeral=COMMANDS_EPHEMERAL)


@tree.command(name="stat", description="Записать статистику за этап")
@app_commands.describe(
    round_number="Этап: 1, 2 или 3",
    kills="Убийства",
    deaths="Смерти",
    score="Счет"
)
async def stat(interaction: discord.Interaction, round_number: int, kills: int, deaths: int, score: int):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    if not can_track_today():
        await interaction.followup.send(
            "❌ Сегодня учет не ведется. Админ может включить его командой /начатьучет.",
            ephemeral=True
        )
        return

    if round_number not in [1, 2, 3]:
        await interaction.followup.send("❌ Этап должен быть 1, 2 или 3.", ephemeral=True)
        return

    if kills < 0 or deaths < 0 or score < 0:
        await interaction.followup.send("❌ Значения не могут быть отрицательными.", ephemeral=True)
        return

    await queue_write({
        "type": "stat",
        "nick": interaction.user.display_name,
        "round": round_number,
        "kills": kills,
        "deaths": deaths,
        "score": score
    })

    await interaction.followup.send(
        f"✅ Статистика принята: {round_number} этап, {kills}/{deaths}, счет {score}",
        ephemeral=COMMANDS_EPHEMERAL
    )


@tree.command(name="adminhere", description="Админ-отметка игрока как присутствующего")
@app_commands.describe(nick="Ник игрока")
@app_commands.checks.has_permissions(manage_guild=True)
async def admin_here(interaction: discord.Interaction, nick: str):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    if not can_track_today():
        await interaction.followup.send(
            "❌ Сегодня учет не ведется. Сначала используй /начатьучет.",
            ephemeral=True
        )
        return

    await queue_write({
        "type": "mark",
        "nick": nick,
        "status": "был",
        "reason": "-",
        "time": current_time()
    })

    await interaction.followup.send(
        f"✅ Игрок отмечен как присутствующий: {normalize_nick(nick)}",
        ephemeral=COMMANDS_EPHEMERAL
    )


@tree.command(name="admincant", description="Админ-отметка отсутствия игрока")
@app_commands.describe(nick="Ник игрока", reason="Причина отсутствия")
@app_commands.checks.has_permissions(manage_guild=True)
async def admin_cant(interaction: discord.Interaction, nick: str, reason: str):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    if not can_track_today():
        await interaction.followup.send(
            "❌ Сегодня учет не ведется. Сначала используй /начатьучет.",
            ephemeral=True
        )
        return

    await queue_write({
        "type": "mark",
        "nick": nick,
        "status": "не был",
        "reason": reason,
        "time": current_time()
    })

    await interaction.followup.send(
        f"✅ Игрок отмечен как отсутствующий: {normalize_nick(nick)}",
        ephemeral=COMMANDS_EPHEMERAL
    )


@tree.command(name="когонет", description="Показать кто сегодня не отметился")
async def who_missing(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    try:
        await flush_writes()
        await interaction.followup.send(build_missing_report(), ephemeral=COMMANDS_EPHEMERAL)
    except Exception as e:
        await interaction.followup.send(f"❌ Ошибка: {e}", ephemeral=True)


@tree.command(name="add", description="Добавить игрока в конец состава")
@app_commands.describe(nick="Ник игрока")
@app_commands.checks.has_permissions(manage_guild=True)
async def add_player(interaction: discord.Interaction, nick: str):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    added = add_player_to_sheet(nick)

    text = (
        f"✅ Игрок добавлен: {normalize_nick(nick)}"
        if added
        else f"⚠️ Игрок уже есть: {normalize_nick(nick)}"
    )

    await interaction.followup.send(text, ephemeral=COMMANDS_EPHEMERAL)


@tree.command(name="кик", description="Удалить игрока из состава")
@app_commands.describe(nick="Ник игрока")
@app_commands.checks.has_permissions(manage_guild=True)
async def kick_player(interaction: discord.Interaction, nick: str):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    removed = kick_player_from_sheet(nick)

    text = (
        f"✅ Игрок удален: {normalize_nick(nick)}"
        if removed
        else f"⚠️ Игрок не найден: {normalize_nick(nick)}"
    )

    await interaction.followup.send(text, ephemeral=COMMANDS_EPHEMERAL)


@tree.command(name="players", description="Показать список игроков")
async def players_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    players = get_players()
    text = "⚠️ Список пуст." if not players else "📋 Игроки:\n" + "\n".join(f"- {p}" for p in players)

    await interaction.followup.send(text[:1900], ephemeral=COMMANDS_EPHEMERAL)


@tree.command(name="начатьучет", description="Принудительно создать сегодняшний лист учета")
@app_commands.checks.has_permissions(manage_guild=True)
async def start_tracking(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    sheet = get_or_create_today_sheet()

    await interaction.followup.send(
        f"✅ Учет на сегодня начат. Лист: {sheet.title}",
        ephemeral=COMMANDS_EPHEMERAL
    )


@tree.command(name="cleartoday", description="Очистить сегодняшний лист и пересоздать из шаблона")
@app_commands.checks.has_permissions(manage_guild=True)
async def clear_today(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    sheet = recreate_today_sheet()

    await interaction.followup.send(
        f"✅ Сегодняшний лист пересоздан: {sheet.title}",
        ephemeral=COMMANDS_EPHEMERAL
    )


@tree.command(name="createday", description="Создать лист дня по дате")
@app_commands.describe(date_text="Дата ДД.ММ.ГГГГ")
@app_commands.checks.has_permissions(manage_guild=True)
async def create_day_by_date(interaction: discord.Interaction, date_text: str):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    try:
        sheet = get_or_create_sheet_by_date(date_text)
        await interaction.followup.send(f"✅ Лист готов: {sheet.title}", ephemeral=COMMANDS_EPHEMERAL)
    except Exception as e:
        await interaction.followup.send(f"❌ Ошибка: {e}", ephemeral=True)


@tree.command(name="clearday", description="Пересоздать день из шаблона")
@app_commands.describe(date_text="Дата ДД.ММ.ГГГГ")
@app_commands.checks.has_permissions(manage_guild=True)
async def clear_day_by_date(interaction: discord.Interaction, date_text: str):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    try:
        sheet = recreate_sheet_by_date(date_text)
        await interaction.followup.send(f"✅ День пересоздан: {sheet.title}", ephemeral=COMMANDS_EPHEMERAL)
    except Exception as e:
        await interaction.followup.send(f"❌ Ошибка: {e}", ephemeral=True)


@tree.command(name="flush", description="Записать очередь в таблицу")
async def flush_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=COMMANDS_EPHEMERAL)

    try:
        count = await flush_writes()
        await interaction.followup.send(f"✅ Записано действий: {count}", ephemeral=COMMANDS_EPHEMERAL)
    except Exception as e:
        await interaction.followup.send(f"❌ Ошибка: {e}", ephemeral=True)


@tasks.loop(seconds=FLUSH_INTERVAL_SECONDS)
async def queue_flusher():
    try:
        await flush_writes()
    except Exception as e:
        print(f"Ошибка фоновой записи: {e}")


@tasks.loop(minutes=1)
async def daily_report():
    if not ENABLE_MISSING_REPORT:
        return

    if not is_war_day() and not today_sheet_exists():
        return

    now = now_dt()
    h, m = parse_time(REPORT_TIME)

    if now.hour != h or now.minute != m:
        return

    try:
        await flush_writes()

        channel = bot.get_channel(REPORT_CHANNEL_ID)

        if channel:
            await channel.send(build_missing_report())
    except Exception as e:
        print(f"Ошибка ежедневного отчета: {e}")


bot.run(DISCORD_TOKEN)