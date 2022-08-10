import logging

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
logging.basicConfig(
    format = '%(asctime)s - (%(filename)s:%(lineno)d) %(levelname)s(%(name)s): %(message)s',
    filename = 'app.log')

def info_log(bot, msg, groupid):
    logger.info(msg)
    message = bot.send_message(groupid, f"<i>{msg}</i>")
    return message

def exception(bot, msg, e, groupid):
    logger.exception(msg)
    bot.send_message(groupid, f"❌ <i>{msg}</i>\n\n<code>{e}</code>")