from telebot import TeleBot
from telebot.types import InlineKeyboardButton
from telebot.types import InlineKeyboardMarkup

from utils.db import Db
from utils import autodelete

from time import time
from datetime import datetime, timedelta

from random import sample, shuffle
from PIL import Image, ImageDraw, ImageFont

def restrict_chat_member(bot: TeleBot, chat_id: int, user_id: int):
    return bot.restrict_chat_member(
        chat_id, user_id,
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False,
    )

def unrestrict_chat_member(bot: TeleBot, chat_id: int, user_id: int):
    return bot.restrict_chat_member(
        chat_id, user_id,
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_change_info=True,
        can_invite_users=True,
        can_pin_messages=True,
    )

background = Image.open(r"assets/template.png")

font = ImageFont.truetype(r"assets/emoji.ttf", 200)

emojis = [
    '😀', '😅', '😇', '😉', '😍', '😜', '🤑', '😎', '🤡', '😡', '😵', '🤔', '🤥', '🤐', '😈',

    '💩', '👻', '👽', '🎃', '😺', '👀', '👑', '🙏🏻', '✌🏻', '🎅🏻', '🐶', '🐱', '🐭', '🐹', '🦊',

    '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐽', '🐸', '🐵', '🐔', '🐤', '🦆', '🦉', '🦇', '🎀',

    '🐌', '🐚', '🐬', '🍀', '🌎', '💫', '⭐️', '✨', '🔥', '🌈', '❄️', '💦', '🥂', '🍎', '🍐',

    '🍊', '🍋', '🍌', '🍉', '🍒', '🍑', '🥝', '🥑', '🍆', '🥕', '🥜', '🍗', '🍕', '🌭', '🍔',

    '🍙', '🍬', '⚽️', '🏀', '🏈', '🏓', '🥋', '🏅', '🎨', '🎲', '🎯', '🎳', '🚗', '🛵', '🚂',

    '🚀', '🏠', '📞', '☎️', '⏰', '⌛️', '💡', '💵', '💎', '⚖️', '⚙️', '💣', '💊', '🔑', '🎁',

    '🎉', '📦', '📃', '📂', '🔖', '📌', '✒️', '✏️', '🔍', '🔒', '👺', '🦋', '🍟', '✈️', '🎈',
]

def send_captcha(bot:TeleBot, user_id:int, grp_id:int):

    captcha = background.copy()

    emoji = ImageDraw.Draw(captcha)

    options = sample(emojis, 15)

    correct = sample(options, 6)

    incorrect = list(set(options) - set(correct))

    positions = [
        (20, 50), (20, 300), (320, 50),
        (320, 300), (620, 50), (620, 300)
    ]

    for __, _ in enumerate(correct):
        emoji.text(positions[__], _, font=font, embedded_color=True)

    markup = InlineKeyboardMarkup(row_width=5)

    correct_buttons = [InlineKeyboardButton(_, callback_data=f"correct:{__}:{user_id}") for __, _ in enumerate(correct, 1)]

    incorrect_buttons = [InlineKeyboardButton(_, callback_data=f"incorrect:{__}:{user_id}") for __, _ in enumerate(incorrect, 1)]

    buttons = correct_buttons + incorrect_buttons

    shuffle(buttons)
    markup.add(*buttons)

    return bot.send_photo(grp_id, captcha, reply_markup=markup)

def captcha_timeout(bot:TeleBot, grp_id:int, database:Db):

    users = database.select(f"SELECT * FROM Captcha WHERE time < ?", int(round(time())))

    if users:
        for user in users:
            msg = bot.send_message(grp_id, f"<b>❌ <a href='tg://user?id={user[0]}'>USER 👽</a> VERIFICATION TIMEOUT ❌\n\
                    \nThey have been removed from the group!\n\nThey can try joining again after 24 hours ⏳</b>")
            bot.ban_chat_member(grp_id, user[0], until_date=datetime.now() + timedelta(minutes=5), revoke_messages=False)
            database.query(f"DELETE FROM Captcha WHERE Uid = {user[0]}", commit=True)
            autodelete(bot, msg)
