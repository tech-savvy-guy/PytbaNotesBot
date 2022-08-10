from os import getenv

import telebot
from telebot.types import Message
from telebot.util import extract_arguments

from utils import autodelete, has_reply, log

from utils.captcha import send_captcha, captcha_timeout
from utils.captcha import restrict_chat_member, unrestrict_chat_member

from utils.db import Db
from time import time, sleep

import schedule, threading

from datetime import datetime, timedelta

#pip install python-dotenv
try:
    from os.path import dirname, join
    from dotenv import load_dotenv
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except ModuleNotFoundError:
    print('dotenv non è installato')
except:
    pass

db = Db(getenv('DB_NAME'))

bot = telebot.TeleBot(getenv('BOT_TOKEN'), parse_mode = 'HTML')

GROUPID = int(getenv('GROUP_ID'))
STORAGEID = int(getenv('STORAGE_ID'))
cop = 5 #count items on page

# ----------------- CAPTCHA TIMEOUT THREAD ----------------- #

schedule.every(1).minute.do(captcha_timeout, bot, GROUPID, db)

def run_captcha():
    while True:
        schedule.run_pending()
        sleep(1)

captcha_thread = threading.Thread(target=run_captcha)

@bot.message_handler(commands=['allnotes'])
def notes(message: Message):
    if message.chat.id == GROUPID:
        keys = db.select("SELECT Key, Description FROM Notes")
        if keys:
            keys.sort()
            getkeytext = "Use '/get key' - to get note.\n\n<b>Keys:</b>\n"
            for key in keys:
                getkeytext+=f"<code>{str(key[0])}</code> - <i>{str(key[1])}</i>\n"
            msg = bot.send_message(message.chat.id, getkeytext, reply_to_message_id = has_reply(message))
        else:
            msg = bot.send_message(message.chat.id, "There are no keys yet. Use\n'/add_note key description\ntext'")
        bot.delete_message(message.chat.id, message.message_id)
        autodelete(bot, msg)

@bot.message_handler(commands=['notes'])
def notes(message: Message):
    if message.chat.id == GROUPID:
        keys = db.select("SELECT Key, Description FROM Notes")
        if keys:
            keys.sort()
            if len(keys) > cop:
                keys = keys[:cop]
                markup = telebot.types.InlineKeyboardMarkup()
                button1 = telebot.types.InlineKeyboardButton(text="➡️", callback_data=f'r|{cop}')
                markup.add(button1)
                getkeytext = "Use '/get key' - to get note.\n\n<b>Keys:</b>\n"
                for key in keys:
                    getkeytext+=f"<code>{str(key[0])}</code> - <i>{str(key[1])}</i>\n\n"
                msg = bot.send_message(message.chat.id, getkeytext, reply_to_message_id = has_reply(message), reply_markup=markup)
            else:
                getkeytext = "Use '/get key' - to get note.\n\n<b>Keys:</b>\n"
                for key in keys:
                    getkeytext+=f"<code>{str(key[0])}</code> - <i>{str(key[1])}</i>\n\n"
                msg = bot.send_message(message.chat.id, getkeytext, reply_to_message_id = has_reply(message))
        else:
            msg = bot.send_message(message.chat.id, "There are no keys yet. Use\n'/add_note key description\ntext'")
        bot.delete_message(message.chat.id, message.message_id)
        autodelete(bot, msg)

@bot.callback_query_handler(func=lambda callback: callback.message.chat.id == GROUPID)
def callbacks(callback):

    # ------------------ NOTES PAGINATION SYSTEM ------------------ #

    cid = callback.message.chat.id
    mid = callback.message.message_id
    data = callback.data

    if data[:2] == 'r|':
        page = int(data[2:])
        keys = db.select("SELECT Key, Description FROM Notes")
        if keys:
            keys.sort()
            keys = keys[page:]
            if keys:
                if len(keys) > cop:
                    keys = keys[:cop]
                    markup = telebot.types.InlineKeyboardMarkup()
                    button1 = telebot.types.InlineKeyboardButton(text="⬅️", callback_data=f'l|{page-cop}')
                    button2 = telebot.types.InlineKeyboardButton(text="➡️", callback_data=f'r|{page+cop}')
                    markup.add(button1, button2)
                    getkeytext = "Use '/get key' - to get note.\n\n<b>Keys:</b>\n"
                    for key in keys:
                        getkeytext+=f"<code>{str(key[0])}</code> - <i>{str(key[1])}</i>\n\n"
                    msg = bot.edit_message_text(chat_id=cid, message_id=mid, text=getkeytext, reply_markup=markup)
                else:
                    markup = telebot.types.InlineKeyboardMarkup()
                    button1 = telebot.types.InlineKeyboardButton(text="⬅️", callback_data=f'l|{page-cop}')
                    markup.add(button1)
                    getkeytext = "Use '/get key' - to get note.\n\n<b>Keys:</b>\n"
                    for key in keys:
                        getkeytext+=f"<code>{str(key[0])}</code> - <i>{str(key[1])}</i>\n\n"
                    msg = bot.edit_message_text(chat_id=cid, message_id=mid, text=getkeytext, reply_markup=markup)
    
    if data[:2] == 'l|':
        page = int(data[2:])
        keys = db.select("SELECT Key, Description FROM Notes")
        if keys:
            keys.sort()
            if page > 1:
                keys = keys[page:]
                if keys:
                    keys = keys[:cop]
                    if keys:
                        markup = telebot.types.InlineKeyboardMarkup()
                        button1 = telebot.types.InlineKeyboardButton(text="⬅️", callback_data=f'l|{page-cop}')
                        button2 = telebot.types.InlineKeyboardButton(text="➡️", callback_data=f'r|{page+cop}')
                        markup.add(button1, button2)
                        getkeytext = "Use '/get key' - to get note.\n\n<b>Keys:</b>\n"
                        for key in keys:
                            getkeytext+=f"<code>{str(key[0])}</code> - <i>{str(key[1])}</i>\n\n"
                        msg = bot.edit_message_text(chat_id=cid, message_id=mid, text=getkeytext, reply_markup=markup)
            else:
                keys = keys[:cop]
                markup = telebot.types.InlineKeyboardMarkup()
                button1 = telebot.types.InlineKeyboardButton(text="➡️", callback_data=f'r|{cop}')
                markup.add(button1)
                getkeytext = "Use '/get key' - to get note.\n\n<b>Keys:</b>\n"
                for key in keys:
                    getkeytext+=f"<code>{str(key[0])}</code> - <i>{str(key[1])}</i>\n\n"
                msg = bot.edit_message_text(chat_id=cid, message_id=mid, text=getkeytext, reply_markup=markup)

    # ------------------ HUMAN VERIFICATION SYSTEM ------------------ #

    chat_id = callback.message.chat.id
    msg_id = callback.message.message_id
    user_id = callback.from_user.id
    data = callback.data

    if data[:6] == 'verify':
        if str(user_id) != data.split(":")[-1]:
            bot.answer_callback_query(callback.id, "This message is not for you 😐", True)
        else:
            bot.delete_message(chat_id, msg_id)
            autodelete(bot, send_captcha(bot, user_id, GROUPID), 35)

    elif data[:7] == "correct":

        if int(data.split(":")[-1]) == user_id:

            keyboard = callback.message.json["reply_markup"]["inline_keyboard"]

            keyboard = keyboard[0] + keyboard[1] + keyboard[2]

            emojis = [_["text"] for _ in keyboard]

            if emojis.count("✅") == 5:
                bot.delete_message(GROUPID, msg_id)
                unrestrict_chat_member(bot, GROUPID, user_id)
                db.query(f"DELETE FROM Captcha WHERE Uid = {user_id}", commit=True)
                msg = bot.send_message(GROUPID, f"<b>VERIFICATION PASSED ✅\n\
                    \nHello [<a href='tg://user?id={user_id}'>{callback.from_user.first_name}</a>]\n\
                    \nWelcome to <a href='https://pytba.readthedocs.org'>pyTelegramBotAPI</a>'s official group chat!\n\
                    \nRead the documentation before asking questions.\n\
                    \nFollow the <a href='https://t.me/c/1060639878/166306'>rules</a> of the group.</b>", 
                    disable_web_page_preview=True, disable_notification=True)
                autodelete(bot, msg)
            else:
                buttons = []
                for _ in keyboard:
                    if _["callback_data"] == data:
                        buttons.append(telebot.types.InlineKeyboardButton("✅", callback_data="done"))
                    else:
                        buttons.append(
                            telebot.types.InlineKeyboardButton(_["text"], callback_data=_["callback_data"]))
                markup = telebot.types.InlineKeyboardMarkup(row_width=5)
                bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=markup.add(*buttons))

        else: bot.answer_callback_query(callback.id, "This message is not for you 😐", True)

    elif data[:9] == "incorrect":

        if int(data.split(":")[-1]) == user_id:

            keyboard = callback.message.json["reply_markup"]["inline_keyboard"]

            keyboard = keyboard[0] + keyboard[1] + keyboard[2]

            emojis = [_["text"] for _ in keyboard]

            if emojis.count("❌") == 2:
                bot.delete_message(GROUPID, msg_id)
                db.query(f"DELETE FROM Captcha WHERE Uid = {user_id}", commit=True)
                msg = bot.send_message(GROUPID, f"<b>VERIFICATION FAILED ❌\n\
                    \n[<a href='tg://user?id={user_id}'>{callback.from_user.first_name}</a>] have been removed from the group!\n\
                    \nThey can try joining again after 24 hours ⏳</b>")
                bot.ban_chat_member(GROUPID, user_id,
                    until_date=datetime.now() + timedelta(days=1), revoke_messages=False)
                autodelete(bot, msg)
            else:
                buttons = []
                for _ in keyboard:
                    if _["callback_data"] == data:
                        buttons.append(telebot.types.InlineKeyboardButton("❌", callback_data="fail"))
                    else:
                        buttons.append(
                            telebot.types.InlineKeyboardButton(_["text"], callback_data=_["callback_data"]))
                markup = telebot.types.InlineKeyboardMarkup(row_width=5)
                bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=markup.add(*buttons))

        else: bot.answer_callback_query(callback.id, "This message is not for you 😐", True)

@bot.message_handler(commands=['get'])
def get_value(message: Message):
    if message.chat.id == GROUPID:
        a = extract_arguments(message.text)
        if a:
            key = db.select("SELECT Mid FROM Notes WHERE key = ?", str(a))
            if key:
                msg = bot.copy_message(message.chat.id, STORAGEID, int(key[0][0]),
                    reply_to_message_id=has_reply(message))
            else:
                msg = bot.send_message(message.chat.id,
                "<b>Note with this key isn't available ❌\n/notes\n/allnotes</b>")
        else:
            msg = bot.send_message(message.chat.id, "<b>Use /get key - to get note.</b>")
        bot.delete_message(message.chat.id, message.message_id)
        autodelete(bot, msg)

@bot.message_handler(commands=['add_note'])
def add_notes(message: Message):
    if message.chat.id == GROUPID:
        admin = db.select("SELECT Uid FROM Admins WHERE Uid = ?", message.from_user.id)
        if admin:
            if has_reply(message):
                argument = extract_arguments(message.text)
                if argument:
                    params = argument.split(maxsplit=1)
                    if len(params) == 1:
                        msg = bot.send_message(message.chat.id, "<b>You forgot the description ❌</b>")
                    else:
                        key, desc = params
                        iskey = db.select("SELECT Mid FROM Notes WHERE Key = ?", key)
                        if iskey:
                            msg = bot.send_message(message.chat.id,
                                "<b>Note with this key already exists ❌\n\
                                \nTry again with another key.</b>")
                        else:
                            mid = bot.copy_message(STORAGEID, message.chat.id, has_reply(message)).message_id
                            db.query("INSERT INTO Notes(Key, Description, Mid) VALUES(?, ?, ?)",
                                key, desc, mid, commit=True)
                            msg = bot.send_message(message.chat.id,
                                "Note successfully added with key <code>{}</code> ✅".format(key))                            
                else:
                    msg = bot.send_message(message.chat.id, "<b>You forgot the key ❌</b>")
            else:
                msg = bot.send_message(message.chat.id, "<b>You forgot to reply to a message ❌</b>")
        else:
            msg = bot.send_message(message.chat.id, "<b>You're not a moderator ❌</b>")
        autodelete(bot, msg, 2)
        autodelete(bot, message, 2)

@bot.message_handler(commands=['delete_note'])
def delete_notes(message):
    if message.chat.id == GROUPID:
        admin = db.select("SELECT Uid FROM Admins WHERE Uid = ?", message.from_user.id)
        if admin:
            a = extract_arguments(message.text)
            if a:
                key = db.select("SELECT * FROM Notes WHERE Key = ?", str(a))
                if key:
                    db.query("DELETE FROM Notes WHERE Key = ?", str(a), commit = True)
                    bot.delete_message(STORAGEID, key[0][-1])
                    msg = bot.send_message(message.chat.id, "<b>Note with key <code>{}</code> successfully deleted ✅</b>".format(a))
                else:
                    msg = bot.send_message(message.chat.id, "<b>Note with key <code>{}</code> isn't available ❌</b>".format(a))
            else:
                msg = bot.send_message(message.chat.id, "<b>You forgot the key ❌</b>")
        else:
            msg = bot.send_message(message.chat.id, "<b>You're not a moderator ❌</b>")
        autodelete(bot, msg, 2)
        autodelete(bot, message, 0)

@bot.message_handler(commands=['add_admin'])
def add_admins(message: Message):
    if message.chat.id == GROUPID:
        admin = db.select("SELECT Uid FROM Admins WHERE Uid = ?", message.from_user.id)
        if admin:
            if message.reply_to_message:
                admin2 = db.select("SELECT Uid FROM Admins WHERE Uid = ?", message.reply_to_message.from_user.id)
                if admin2:
                    msg = bot.send_message(message.chat.id, "<b>This user is already a moderator ❌</b>")
                else:
                    db.query("INSERT INTO Admins(Uid) VALUES(?)", message.reply_to_message.from_user.id, commit = True)
                    msg = bot.send_message(message.chat.id,
                    f"<b><a href='tg://user?id={message.reply_to_message.from_user.id}'>This</a> user has now successfully become a moderator ✅</b>")
            else:
                msg = bot.send_message(message.chat.id, "<b>This command must be a reply to the user ❌</b>")
        else:
            msg = bot.send_message(message.chat.id, "<b>You're not a moderator ❌</b>")
        autodelete(bot, msg, 2)
        autodelete(bot, message, 1)

@bot.message_handler(commands=['help'])
def help_func(message):
    if message.chat.id == GROUPID:
        msg = bot.send_message(message.chat.id,
        "<b>Usage:\n\
        \n/notes - list of notes\n\
        \n/allnotes - list of all notes\n\
        \n/add_note - add new note\n\
        \n/delete_note - delete note\n\
        \n/get - get note\n\
        \n/add_admin - add new moderator\n\
        \n@pytbanotes - view all notes</b>")
        autodelete(bot, msg, 2)
        autodelete(bot, message, 0)

@bot.message_handler(commands=['start'])
def welcome(message: Message):
    if message.chat.id == GROUPID:
        msg = bot.send_message(message.chat.id, "<b>Hi, I'm online!\n\nSend /help</b>")
        autodelete(bot, msg, 0.5)
    elif message.chat.type == 'private':
        bot.send_message(message.chat.id, 
        "<b>Join <a href='https://telegram.me/joinchat/Bn4ixj84FIZVkwhk2jag6A'>pyTelegramBotAPI's Telegram Group</a> to get code snippets!</b>")
    autodelete(bot, message, 0)

@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    if message.chat.id == GROUPID:
        isbot = message.new_chat_members[0].is_bot
        telegram_id = message.new_chat_members[0].id
        if isbot:
            bot.ban_chat_member(GROUPID, telegram_id)
        else:
            db.query("INSERT INTO Captcha (Uid, time) VALUES (?, ?)",
                telegram_id, int(round(time())) + 30 * 60, commit=True)
            restrict_chat_member(bot, GROUPID, telegram_id)
            bot.send_message(GROUPID, f"<b>Hello [<a href='tg://user?id={telegram_id}'>{message.from_user.first_name}</a>]\n\
                \nWelcome to <a href='https://pytba.readthedocs.org'>pyTelegramBotAPI</a>'s official group chat!\n\
                \nTo get started verify that you're a human!</b>", reply_markup=telebot.types.InlineKeyboardMarkup().row(
                telebot.types.InlineKeyboardButton("🟢 VERIFY NOW 🟢", callback_data=f"verify:{telegram_id}")),
                disable_notification=True, disable_web_page_preview=True)

@bot.message_handler(content_types=['left_chat_member'])
def left_member(message):
    db.query(f"DELETE FROM Captcha WHERE Uid = {message.left_chat_member.id}", commit=True)

msg = log.info_log(bot, "I'm started! 🤖", GROUPID)
autodelete(bot, msg, 1)

captcha_thread.start()
bot.infinity_polling(skip_pending=True)
