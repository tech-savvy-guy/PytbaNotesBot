from threading import Timer, Thread

import telebot
from telebot import TeleBot
from telebot.types import Message


def has_reply(msg: Message):
    "Pass a Message object. If it replies to a message, function will return the message_id, else None"
    
    if msg.reply_to_message:
        return msg.reply_to_message.id
    else: return None

def autodelete(bot: TeleBot, msg: telebot.types.Message, time = 15):
    "Function to start timer. It'll delete a message after 15 minutes, or any time passed to function"
    
    Timer(60 * time, bot.delete_message, (msg.chat.id, msg.message_id)).start()
    