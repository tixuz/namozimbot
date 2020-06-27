# -*- coding: utf-8 -*-
from config import namozbottoken, namozapibase

bot_token = namozbottoken
api_base = namozapibase
auth_token = ""
arr = {}

import re
import telebot
from telebot import types
import datetime
from datetime import timezone
import requests
import copy
hindol = 505392203



InlineKeyboardButton = types.InlineKeyboardButton
InlineKeyboardMarkup = types.InlineKeyboardMarkup

bot = telebot.TeleBot(bot_token)


# Browse list of Regions
# goto last visited region
# goto last visited district
# goto last visited school
# goto last visited class
# Region Name, Code
# Browse list of Districts
# Browse list of Schools
# Choose school by code
# /region 123123123
# /district 123123123
# /school 123123123
# Browse list of classes
# Add Students
# /addstudents 2020-06-16
# first_name;middle_name;last_name;year;month;day;identity_document

def extract_region(arg):
    return arg.lstrip('/region ')  # to work with command arguments


@bot.message_handler(commands=['start', 'help'])
def myhelp(message):
    answer = help_menu(bot, message, auth_token, api_base)
    bot.send_message(chat_id=answer["chat_id"],
                     text=answer["text"],
                     parse_mode=answer["parse_mode"],
                     reply_markup=answer["reply_markup"])


def help_menu(bot, message, auth_token, api_base, reply_markup=None):
    # this part is for handling arr[], TG name and API data to arr[] #start
    global arr
    bot_id = int(bot.get_me().id)
    chat_id = message.chat.id
    auth_token = auth_token
    api_base = api_base
    tg_first_name = (message.chat.first_name) if message.chat.first_name is not None else "NoFirstName"
    tg_last_name = (message.chat.last_name) if message.chat.last_name is not None else "NoLastName"
    if not bot_id in arr:
        arr[bot_id] = {}
    if not chat_id in arr[bot_id]:
        arr[bot_id][chat_id] = {}
    tg_user = str(chat_id) + ": " + tg_first_name + " " + tg_last_name
    if not 'tg_user' in arr[bot_id][chat_id]:
        arr[bot_id][chat_id]['tg_user'] = tg_user
    if not 'auth_token' in arr[bot_id][chat_id]:
        arr[bot_id][chat_id]['auth_token'] = auth_token
    if not 'api_base' in arr[bot_id][chat_id]:
        arr[bot_id][chat_id]['api_base'] = api_base
    # this part is for handling TG name and API data to arr[] #end

    keyboard = InlineKeyboardMarkup(row_width=1)
    url_button = InlineKeyboardButton(text="Men ham namoz o'qiyman (ziyouz)", callback_data="/menhamuz")
    help_button = InlineKeyboardButton(text="Я тоже умею совершать намаз", callback_data="/menham")
    callback_button = InlineKeyboardButton(text="Arab yozuvi", callback_data="/arab")
    row = [url_button, help_button, callback_button]
    keyboard.add(*row)
    reply_markup = keyboard
    answer = {'chat_id': chat_id,
              'parse_mode': None,
              'text': help_menu_message(bot, message),
              'reply_markup': reply_markup}
    return answer


def help_menu_message(bot, message):
    # this message does not go to API
    global arr
    bot_id = int(bot.get_me().id)
    chat_id = message.chat.id
    message_id = message.message_id
    text = "Message # %s" % int(message_id)
    text += "\n🤖 Assalomu alaykum, " + arr[bot_id][chat_id]['tg_user'] + "!\n"
    text += "\n🤖 Namoz vaqtini bilish uchun lokatsiyani yuboring\n"
    text += "====💭BUYRUQLAR💭====\n"
    text += "/namoz - Namoz vaqtini bilish (lokatsiyani yuborish orqali)\n"
    text += "/menhamuz - Men ham namoz o'qishni bilaman (ziyouz) kitobini yuklab olish\n"
    text += "/menham - Я тоже умею совершать намаз kitobini yuklab olish\n"
    text += "/arab  - Пропись арабского языка китобини yuklab olish\n"
    text += "Namoz vaqtini bilish uchun, iltimos, lokatsiyani yuboring\n"

    return text


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    print(message)


@bot.message_handler(commands=['namoz'])
def mynamoz(message):
    global arr
    bot_id = int(bot.get_me().id)
    chat_id = message.chat.id
    initialize_arr(bot, message, auth_token, api_base)
    tg_user = arr[bot_id][chat_id]['tg_user']
    print("namoz:" + tg_user)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Joylashuvingizni yuboring | Отправить местоположение",
                                      request_location=True)
    keyboard.add(button_geo)
    bot.send_message(chat_id, "Joylashuvingizni yuboring | Отправить местоположение", reply_markup=keyboard)


@bot.message_handler(content_types=["location"])
def mylocation(message):
    bot_id = int(bot.get_me().id)
    chat_id = message.chat.id
    bot.send_location(hindol, message.location.latitude, message.location.longitude)
    tg_first_name = (message.chat.first_name) if message.chat.first_name is not None else "NoFirstName"
    tg_last_name = (message.chat.last_name) if message.chat.last_name is not None else "NoLastName"
    tg_user = str(chat_id) + ": " + tg_first_name + " " + tg_last_name
    bot.send_message(hindol, tg_user)
    if message.location is not None:
        print(message.location)
        url = api_base + "latitude={}&longitude={}".format(message.location.latitude, message.location.longitude)
        print(url)
        response = requests.get(url)
        print(url)
#        print(response.json())
        print("latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude))
        now = datetime.datetime.now(timezone.utc)
        today = "%s" % (now.strftime("%d-%m-%Y"))
        thistime = "%s" % (now.strftime("%H-%M"))

        thistimep = "%s" % (now.strftime("%H:%M"))
        timings = response.json()['data']
        text = ""
        for tayming in timings:
            timing = tayming['timings']
   #         MYTMZ = tayming['meta']['timezone']
            timediff = re.search(r'\((.)(\d\d)\)',timing['Sunrise'])
            thishour = str(int("%s" % (now.strftime("%H"))))
            herehour = thishour
            if (timediff.group(1) is not None) and (timediff.group(2) is not None):
                herehour = str(eval("(" + thishour + timediff.group(1) + str(int(timediff.group(2))) + ")")).zfill(2)
            heremin = str(int("%s" % (now.strftime("%M"))))
            thistime = herehour + "-" + heremin.zfill(2)
            thistimep = herehour + ":" + heremin.zfill(2)



     #       thistime = "%s" % datetime.datetime.now(timezone.utc).astimezone(MYTMZ).strftime("%H-%M")
      #      thistimep = "%s" % datetime.datetime.now(timezone.utc).astimezone(MYTMZ).strftime("%H:%M")
            if (today == tayming['date']['gregorian']['date']):

                if thistimep > timing['Fajr'][:-6] and thistime <= timing['Sunrise'][:-6]:
                    text = "*Hozir {}:* Bomdod (Fajr) vaqti\n".format(thistimep)
                if thistimep > timing['Sunrise'][:-6] and thistime <= timing['Dhuhr'][:-6]:
                    text = "*Hozir {}:* Choshtgoh (Zuho) vaqti\n".format(thistimep)
                if thistimep > timing['Dhuhr'][:-6] and thistime <= timing['Asr'][:-6]:
                    text = "*Hozir {}:* Peshin (Zuhr) vaqti\n".format(thistimep)
                if thistimep > timing['Asr'][:-6] and thistime <= timing['Sunset'][:-6]:
                    text = "*Hozir {}:* Asr vaqti\n".format(thistimep)
                if thistimep > timing['Sunset'][:-6] and thistime <= timing['Isha'][:-6]:
                    text = "*Hozir {}:* Shom (Mag'rib' vaqti\n".format(thistimep)
                if thistimep > timing['Isha'][:-6]:
                    text = "*Hozir {}:* Xufton (Isho') vaqti\n".format(thistimep)
                text += "*Bugun:* " + today + "\n*Bomdod:* {}\n*Quyosh:* {}\n*Peshin:* {} \n*Asr:* {}\n*Shom:* {}\n*Xufton:* {}\n" \
                                              "*Namoz vaqti:* Hanafiy\n" \
                                              "*Namoz hisoblash usuli:* Rossiya ulamolar kengashi usuli".format(
                    timing['Fajr'][:-6], timing['Sunrise'][:-6], timing['Dhuhr'][:-6], timing['Asr'][:-6],
                    timing['Sunset'][:-6], timing['Isha'][:-6])
        keyboard = InlineKeyboardMarkup(row_width=1)
        url_button = InlineKeyboardButton(text="Men ham namoz o'qiyman (ziyouz)", callback_data="/menhamuz")
        help_button = InlineKeyboardButton(text="Я тоже умею совершать намаз", callback_data="/menham")
        callback_button = InlineKeyboardButton(text="Arab yozuvi", callback_data="/arab")
        row = [url_button, help_button, callback_button]
        keyboard.add(*row)
        bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', reply_markup=keyboard)


@bot.message_handler(commands=['menham'])
def mymenham(message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    url_button = InlineKeyboardButton(text="Men ham namoz o'qiyman (ziyouz)", callback_data="/menhamuz")
    help_button = InlineKeyboardButton(text="Я тоже умею совершать намаз", callback_data="/menham")
    callback_button = InlineKeyboardButton(text="Arab yozuvi", callback_data="/arab")
    row = [url_button, help_button, callback_button]
    keyboard.add(*row)
    chat_id = message.chat.id
    file_id="BQACAgIAAxkBAAMqXvQ2VgViwYzPK4Q9QCAxxUNpYhoAApMIAAKVV6BLhiVFe0iq1VsaBA"
    bot.send_document(chat_id,file_id,keyboard)

@bot.message_handler(commands=['menhamuz'])
def mymenhamuz(message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    url_button = InlineKeyboardButton(text="Men ham namoz o'qiyman (ziyouz)", callback_data="/menhamuz")
    help_button = InlineKeyboardButton(text="Я тоже умею совершать намаз", callback_data="/menham")
    callback_button = InlineKeyboardButton(text="Arab yozuvi", callback_data="/arab")
    row = [url_button, help_button, callback_button]
    keyboard.add(*row)
    chat_id = message.chat.id
    file_id="BQACAgIAAxkBAAP1XvRKt_Kge5tGTd31i_MazpCPeKAAAjoIAAKBV6hLqy7S6vwjBcsaBA"
    file_id="BQACAgIAAxkBAAP1XvRKt_Kge5tGTd31i_MazpCPeKAAAjoIAAKBV6hLqy7S6vwjBcsaBA"
    bot.send_document(chat_id,file_id,keyboard)

@bot.message_handler(commands=['arab'])
def myarab(message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    url_button = InlineKeyboardButton(text="Men ham namoz o'qiyman (ziyouz)", callback_data="/menhamuz")
    help_button = InlineKeyboardButton(text="Я тоже умею совершать намаз", callback_data="/menham")
    callback_button = InlineKeyboardButton(text="Arab yozuvi", callback_data="/arab")
    row = [url_button, help_button, callback_button]
    keyboard.add(*row)
    chat_id = message.chat.id
    file_id="BQACAgIAAxkBAAMsXvQ4EgQFhD_DQLI6SfguqJFgFJIAApQIAAKVV6BL5CQfoIP9qrEaBA"
    bot.send_document(chat_id,file_id,keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    # print(call)
    if call.message:
        if call.data == "test":  # just a test
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="It's a test button")
            # it's just an alert
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="It's a test!")
        # these three use openemis codes

        elif re.search(r'^\/.+', call.data):  # any command in callback
            # it's just an alert
            possibles = globals().copy()
            possibles.update(locals())
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text="!!!!!Here's what I call: " + call.data)
            command = get_command(possibles, call.data, call.message)
            print('in inline ' + str(command['command']))
            result = command['command'](command['message'])
        else:
            set_date(bot, call)
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text=call.data)  # simply alert the callback code


def initialize_arr(bot, message, auth_token, api_base):
    global arr
    global today
    bot_id = int(bot.get_me().id)
    chat_id = message.chat.id
    tg_first_name = (message.chat.first_name) if message.chat.first_name is not None else "NoFirstName"
    tg_last_name = (message.chat.last_name) if message.chat.last_name is not None else "NoLastName"
    tg_user = str(chat_id) + ":" + tg_first_name + " " + tg_last_name
    if not bot_id in arr:
        arr[bot_id] = {}
    if not chat_id in arr[bot_id]:
        arr[bot_id][chat_id] = {}
    if not 'tg_user' in arr[bot_id][chat_id]:
        arr[bot_id][chat_id]['tg_user'] = tg_user
    if auth_token != "" and (not 'auth_token' in arr[bot_id][chat_id]):
        arr[bot_id][chat_id]['auth_token'] = auth_token
    if api_base != "" and (not 'api_base' in arr[bot_id][chat_id]):
        arr[bot_id][chat_id]['api_base'] = api_base
    return


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):  # this is just a repeater
    answer = help_menu(bot, message, auth_token, api_base)
    bot.send_message(hindol, message.text)
    bot.send_message(chat_id=answer["chat_id"],
                     text=answer["text"],
                     parse_mode=answer["parse_mode"],
                     reply_markup=answer["reply_markup"])


def get_command(possibles, data, message):  # this will be a simple message calling function from callback text
    essage = copy.copy(message)
    #    print(essage)
    commandline = data
    essage.text = commandline
    result = {}
    result['message'] = essage
    command = commandline.split()[0]
    if (len(commandline.split()) == 0):
        command = data
    command = command.lstrip("/")
    print(command)
    method_name = command
    method = possibles.get(method_name)
    if not method:
        method = possibles.get("my" + method_name)
        if not method:
            my_error = 'Buyruq' + method_name + ' mavjud emas; '
            method = possibles.get("repeat_all_messages")
            result['command'] = method
            return result
        else:
            print(method)
            result['command'] = method
            return result
    else:
        print(method)
        result['command'] = method
        return result
if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=100)
