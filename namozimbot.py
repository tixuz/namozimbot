# -*- coding: utf-8 -*-
import copy
import datetime as dt
import logging
import os
import re
from zoneinfo import ZoneInfo

import requests
import telebot
from telebot import types

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None

if load_dotenv:
    load_dotenv()

try:
    from config import namozadmin as _cfg_admin  # backward compatibility
    from config import namozapibase as _cfg_apibase
    from config import namozbottoken as _cfg_token
except Exception:
    _cfg_token = _cfg_apibase = _cfg_admin = None

BOT_TOKEN = os.getenv("NAMOZ_BOT_TOKEN", _cfg_token or "")
API_BASE = os.getenv(
    "NAMOZ_API_BASE",
    _cfg_apibase or "https://api.aladhan.com/v1/calendar?method=14&",
)
ADMIN_CHAT_ID = int(os.getenv("NAMOZ_ADMIN_ID", str(_cfg_admin or "0")))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))

if not BOT_TOKEN:
    raise RuntimeError("Missing bot token. Set NAMOZ_BOT_TOKEN in environment or config.py")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("namozimbot")

InlineKeyboardButton = types.InlineKeyboardButton
InlineKeyboardMarkup = types.InlineKeyboardMarkup
bot = telebot.TeleBot(BOT_TOKEN)
arr = {}

TEXTS = {
    "uz": {
        "hello": "Assalomu alaykum",
        "send_location": "Namoz vaqtini bilish uchun lokatsiyani yuboring",
        "commands": "BUYRUQLAR",
        "namoz_button": "Namoz vaqtlari",
        "namoz_cmd": "/namoz - Namoz vaqtini bilish",
        "help_cmd": "/yordam - Yordam olish",
        "settings_cmd": "/settings - Sozlamalar",
        "send_location_btn": "Joylashuvingizni yuboring",
        "location_missing": "Lokatsiya topilmadi. Iltimos, qayta yuboring.",
        "api_error": "API xatoligi",
        "api_bad_json": "API noto'g'ri javob qaytardi. Keyinroq urinib ko'ring.",
        "today_not_found": "Bugungi namoz vaqtlari topilmadi.",
        "help": "Yordam",
        "nearby_mosques": "Yaqin atrofdagi masjidlar",
        "settings_title": "Sozlamalar",
        "language": "Til",
        "asr_mode": "Asr usuli",
        "asr_early": "Erta Asr (Standard)",
        "asr_delayed": "Kech Asr (Hanafi)",
        "saved": "Saqlandi",
        "now_prefix": "Hozir",
        "today": "Bugun",
        "fajr": "Bomdod",
        "sunrise": "Quyosh",
        "dhuhr": "Peshin",
        "asr": "Asr",
        "sunset": "Shom",
        "isha": "Xufton",
        "prayer_time": "Namoz vaqti",
        "calculation": "Namoz hisoblash usuli",
        "calc_value": "Rossiya ulamolar kengashi usuli",
    },
    "tr": {
        "hello": "Selamun aleykum",
        "send_location": "Namaz vakitleri için konumunuzu gönderin",
        "commands": "KOMUTLAR",
        "namoz_button": "Namaz vakitleri",
        "namoz_cmd": "/namoz - Namaz vakitlerini öğren",
        "help_cmd": "/help - Yardım",
        "settings_cmd": "/settings - Ayarlar",
        "send_location_btn": "Konumunu gönder",
        "location_missing": "Konum bulunamadı. Lütfen tekrar gönderin.",
        "api_error": "API hatası",
        "api_bad_json": "API geçersiz yanıt döndürdü. Lütfen sonra tekrar deneyin.",
        "today_not_found": "Bugünkü namaz vakitleri bulunamadı.",
        "help": "Yardım",
        "nearby_mosques": "Yakındaki camiler",
        "settings_title": "Ayarlar",
        "language": "Dil",
        "asr_mode": "İkindi yöntemi",
        "asr_early": "Erken Asr (Standart)",
        "asr_delayed": "Geç Asr (Hanefi)",
        "saved": "Kaydedildi",
        "now_prefix": "Şu an",
        "today": "Bugün",
        "fajr": "İmsak",
        "sunrise": "Güneş",
        "dhuhr": "Öğle",
        "asr": "İkindi",
        "sunset": "Akşam",
        "isha": "Yatsı",
        "prayer_time": "Namaz vakti",
        "calculation": "Hesaplama yöntemi",
        "calc_value": "Rusya Âlimler Konseyi yöntemi",
    },
    "ru": {
        "hello": "Ассаламу алейкум",
        "send_location": "Отправьте геолокацию, чтобы узнать время намаза",
        "commands": "КОМАНДЫ",
        "namoz_button": "Время намаза",
        "namoz_cmd": "/namoz - Узнать время намаза",
        "help_cmd": "/help - Помощь",
        "settings_cmd": "/settings - Настройки",
        "send_location_btn": "Отправить местоположение",
        "location_missing": "Геолокация не найдена. Пожалуйста, отправьте снова.",
        "api_error": "Ошибка API",
        "api_bad_json": "API вернул некорректный ответ. Попробуйте позже.",
        "today_not_found": "Время намаза на сегодня не найдено.",
        "help": "Помощь",
        "nearby_mosques": "Ближайшие мечети",
        "settings_title": "Настройки",
        "language": "Язык",
        "asr_mode": "Метод Асра",
        "asr_early": "Ранний Аср (Стандарт)",
        "asr_delayed": "Поздний Аср (Ханафи)",
        "saved": "Сохранено",
        "now_prefix": "Сейчас",
        "today": "Сегодня",
        "fajr": "Фаджр",
        "sunrise": "Восход",
        "dhuhr": "Зухр",
        "asr": "Аср",
        "sunset": "Магриб",
        "isha": "Иша",
        "prayer_time": "Время намаза",
        "calculation": "Метод расчета",
        "calc_value": "Метод Совета улемов России",
    },
    "en": {
        "hello": "Assalamu alaikum",
        "send_location": "Send your location to get prayer times",
        "commands": "COMMANDS",
        "namoz_button": "Prayer times",
        "namoz_cmd": "/namoz - Get prayer times",
        "help_cmd": "/help - Help",
        "settings_cmd": "/settings - Settings",
        "send_location_btn": "Send location",
        "location_missing": "Location not found. Please send it again.",
        "api_error": "API error",
        "api_bad_json": "API returned an invalid response. Please try again later.",
        "today_not_found": "Today's prayer times were not found.",
        "help": "Help",
        "nearby_mosques": "Nearby mosques",
        "settings_title": "Settings",
        "language": "Language",
        "asr_mode": "Asr method",
        "asr_early": "Early Asr (Standard)",
        "asr_delayed": "Delayed Asr (Hanafi)",
        "saved": "Saved",
        "now_prefix": "Now",
        "today": "Today",
        "fajr": "Fajr",
        "sunrise": "Sunrise",
        "dhuhr": "Dhuhr",
        "asr": "Asr",
        "sunset": "Maghrib",
        "isha": "Isha",
        "prayer_time": "Prayer method",
        "calculation": "Calculation method",
        "calc_value": "Russian Council of Ulama method",
    },
}


def parse_hhmm(raw_value):
    match = re.search(r"(\d{2}):(\d{2})", raw_value or "")
    if not match:
        return None
    return dt.time(hour=int(match.group(1)), minute=int(match.group(2)))


def parse_offset(raw_value):
    match = re.search(r"\(([+-])(\d{2})\)", raw_value or "")
    if not match:
        return dt.timezone.utc
    sign = 1 if match.group(1) == "+" else -1
    hours = int(match.group(2))
    return dt.timezone(dt.timedelta(hours=sign * hours))


def get_now_for_timing(day_data):
    meta = day_data.get("meta", {})
    timezone_name = meta.get("timezone")
    if timezone_name:
        try:
            return dt.datetime.now(ZoneInfo(timezone_name))
        except Exception:
            pass
    tz = parse_offset(day_data.get("timings", {}).get("Sunrise", ""))
    return dt.datetime.now(tz)


def get_today_entry(response_json):
    for day in response_json.get("data", []):
        now_local = get_now_for_timing(day)
        today = now_local.strftime("%d-%m-%Y")
        if day.get("date", {}).get("gregorian", {}).get("date") == today:
            return day, now_local
    return None, None


def get_user_settings(message):
    initialize_arr(message)
    bot_id = int(bot.get_me().id)
    chat_id = message.chat.id
    settings = arr[bot_id][chat_id]
    return settings["lang"], settings["school"]


def t(lang, key):
    return TEXTS.get(lang, TEXTS["uz"]).get(key, TEXTS["uz"][key])


def format_prayer_message(day_data, now_local, lang, school):
    timings = day_data["timings"]
    fajr = parse_hhmm(timings.get("Fajr", ""))
    sunrise = parse_hhmm(timings.get("Sunrise", ""))
    dhuhr = parse_hhmm(timings.get("Dhuhr", ""))
    asr = parse_hhmm(timings.get("Asr", ""))
    sunset = parse_hhmm(timings.get("Sunset", ""))
    isha = parse_hhmm(timings.get("Isha", ""))

    now_time = now_local.time().replace(second=0, microsecond=0)
    now_text = now_local.strftime("%H:%M")
    current_text = f"*{t(lang, 'now_prefix')} {now_text}:* {t(lang, 'isha')}"

    if fajr and sunrise and fajr <= now_time <= sunrise:
        current_text = f"*{t(lang, 'now_prefix')} {now_text}:* {t(lang, 'fajr')}"
    elif sunrise and dhuhr and sunrise < now_time <= dhuhr:
        current_text = f"*{t(lang, 'now_prefix')} {now_text}:* {t(lang, 'sunrise')}"
    elif dhuhr and asr and dhuhr < now_time <= asr:
        current_text = f"*{t(lang, 'now_prefix')} {now_text}:* {t(lang, 'dhuhr')}"
    elif asr and sunset and asr < now_time <= sunset:
        current_text = f"*{t(lang, 'now_prefix')} {now_text}:* {t(lang, 'asr')}"
    elif sunset and isha and sunset < now_time <= isha:
        current_text = f"*{t(lang, 'now_prefix')} {now_text}:* {t(lang, 'sunset')}"

    return (
        f"{current_text}\n"
        f"*{t(lang, 'today')}:* {now_local.strftime('%d-%m-%Y')}\n"
        f"*{t(lang, 'fajr')}:* {timings.get('Fajr', '')[:5]}\n"
        f"*{t(lang, 'sunrise')}:* {timings.get('Sunrise', '')[:5]}\n"
        f"*{t(lang, 'dhuhr')}:* {timings.get('Dhuhr', '')[:5]}\n"
        f"*{t(lang, 'asr')}:* {timings.get('Asr', '')[:5]}\n"
        f"*{t(lang, 'sunset')}:* {timings.get('Sunset', '')[:5]}\n"
        f"*{t(lang, 'isha')}:* {timings.get('Isha', '')[:5]}\n"
        f"*{t(lang, 'prayer_time')}:* {t(lang, 'asr_delayed') if school == 1 else t(lang, 'asr_early')}\n"
        f"*{t(lang, 'calculation')}:* {t(lang, 'calc_value')}"
    )


def help_menu_message(message):
    lang, _ = get_user_settings(message)
    bot_id = int(bot.get_me().id)
    chat_id = message.chat.id
    message_id = message.message_id
    text = f"Message # {int(message_id)}"
    text += f"\n🤖 {t(lang, 'hello')}, {arr[bot_id][chat_id]['tg_user']}!\n"
    text += f"\n🤖 {t(lang, 'send_location')}\n"
    text += f"====💭{t(lang, 'commands')}💭====\n"
    text += f"{t(lang, 'namoz_cmd')}\n"
    text += f"{t(lang, 'help_cmd')}\n"
    text += f"{t(lang, 'settings_cmd')}\n"
    text += f"{t(lang, 'send_location')}\n"
    return text


def help_menu(message):
    lang, _ = get_user_settings(message)
    chat_id = message.chat.id
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text=t(lang, "namoz_button"), callback_data="/namoz"),
        InlineKeyboardButton(text=t(lang, "help"), callback_data="/help"),
        InlineKeyboardButton(text=t(lang, "settings_title"), callback_data="/settings"),
    )
    return {
        "chat_id": chat_id,
        "parse_mode": None,
        "text": help_menu_message(message),
        "reply_markup": keyboard,
    }


def send_help(message):
    answer = help_menu(message)
    bot.send_message(
        chat_id=answer["chat_id"],
        text=answer["text"],
        parse_mode=answer["parse_mode"],
        reply_markup=answer["reply_markup"],
    )


@bot.message_handler(commands=["start", "help", "yordam"])
def myhelp(message):
    send_help(message)


@bot.message_handler(content_types=["document"])
def handle_docs(message):
    logger.info("Received document from chat_id=%s", message.chat.id)


@bot.message_handler(commands=["namoz"])
def mynamoz(message):
    lang, _ = get_user_settings(message)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton(
            text=t(lang, "send_location_btn"),
            request_location=True,
        )
    )
    bot.send_message(
        message.chat.id,
        t(lang, "send_location"),
        reply_markup=keyboard,
    )

@bot.message_handler(commands=["settings"])
def mysettings(message):
    lang, school = get_user_settings(message)
    text = (
        f"⚙️ *{t(lang, 'settings_title')}*\n"
        f"*{t(lang, 'language')}:* {lang.upper()}\n"
        f"*{t(lang, 'asr_mode')}:* {t(lang, 'asr_delayed') if school == 1 else t(lang, 'asr_early')}\n"
    )
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="UZ", callback_data="setlang:uz"),
        InlineKeyboardButton(text="TR", callback_data="setlang:tr"),
        InlineKeyboardButton(text="RU", callback_data="setlang:ru"),
        InlineKeyboardButton(text="EN", callback_data="setlang:en"),
    )
    keyboard.add(
        InlineKeyboardButton(text=t(lang, "asr_early"), callback_data="setschool:0"),
        InlineKeyboardButton(text=t(lang, "asr_delayed"), callback_data="setschool:1"),
    )
    bot.send_message(message.chat.id, text=text, parse_mode="Markdown", reply_markup=keyboard)


@bot.message_handler(content_types=["location"])
def mylocation(message):
    lang, school = get_user_settings(message)
    chat_id = message.chat.id
    if ADMIN_CHAT_ID:
        try:
            bot.send_location(ADMIN_CHAT_ID, message.location.latitude, message.location.longitude)
        except Exception as exc:
            logger.warning("Could not forward location to admin: %s", exc)

    if message.location is None:
        bot.send_message(chat_id, t(lang, "location_missing"))
        return

    url = (
        f"{API_BASE}latitude={message.location.latitude}"
        f"&longitude={message.location.longitude}"
        f"&school={school}"
    )
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        logger.exception("Aladhan API request failed")
        bot.send_message(chat_id, f"{t(lang, 'api_error')}: {exc}")
        return
    except ValueError:
        bot.send_message(chat_id, t(lang, "api_bad_json"))
        return

    today_data, now_local = get_today_entry(payload)
    if not today_data or not now_local:
        bot.send_message(chat_id, t(lang, "today_not_found"))
        return

    text = format_prayer_message(today_data, now_local, lang, school)
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            text=t(lang, "nearby_mosques"),
            url=f"https://www.google.com/maps/search/Mosques/@{message.location.latitude},{message.location.longitude},16z",
        ),
        InlineKeyboardButton(text=t(lang, "help"), callback_data="/help"),
        InlineKeyboardButton(text=t(lang, "settings_title"), callback_data="/settings"),
    )
    bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if not call.message:
        return
    if call.data == "test":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="It's a test button",
        )
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="It's a test!")
        return
    if re.search(r"^\/.+", call.data):
        possibles = globals().copy()
        possibles.update(locals())
        command = get_command(possibles, call.data, call.message)
        command["command"](command["message"])
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
        return
    if call.data.startswith("setlang:"):
        value = call.data.split(":", 1)[1]
        if value in TEXTS:
            initialize_arr(call.message)
            bot_id = int(bot.get_me().id)
            chat_id = call.message.chat.id
            arr[bot_id][chat_id]["lang"] = value
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=t(value, "saved"))
            mysettings(call.message)
            return
    if call.data.startswith("setschool:"):
        value = call.data.split(":", 1)[1]
        if value in ("0", "1"):
            initialize_arr(call.message)
            bot_id = int(bot.get_me().id)
            chat_id = call.message.chat.id
            arr[bot_id][chat_id]["school"] = int(value)
            lang = arr[bot_id][chat_id]["lang"]
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=t(lang, "saved"))
            mysettings(call.message)
            return
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=call.data)


def initialize_arr(message):
    bot_id = int(bot.get_me().id)
    chat_id = message.chat.id
    tg_first_name = message.chat.first_name or "NoFirstName"
    tg_last_name = message.chat.last_name or "NoLastName"
    tg_user = f"{chat_id}: {tg_first_name} {tg_last_name}"

    if bot_id not in arr:
        arr[bot_id] = {}
    if chat_id not in arr[bot_id]:
        arr[bot_id][chat_id] = {}
    if "tg_user" not in arr[bot_id][chat_id]:
        arr[bot_id][chat_id]["tg_user"] = tg_user
    if "lang" not in arr[bot_id][chat_id]:
        arr[bot_id][chat_id]["lang"] = "uz"
    if "school" not in arr[bot_id][chat_id]:
        arr[bot_id][chat_id]["school"] = 1


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    send_help(message)


def get_command(possibles, data, message):
    message_copy = copy.copy(message)
    message_copy.text = data
    result = {"message": message_copy}

    command = (data.split()[0] if data.split() else data).lstrip("/")
    method = possibles.get(command) or possibles.get("my" + command)
    if not method:
        method = possibles.get("repeat_all_messages")
    result["command"] = method
    return result


if __name__ == "__main__":
    bot.polling(none_stop=True, timeout=100)
