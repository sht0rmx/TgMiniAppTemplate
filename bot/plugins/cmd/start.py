from modules.bot_funcs import get_data
from modules.plugins import CommandPlugin
from modules.logging import logger
from modules import bot

def main(plug: CommandPlugin):
    text, markup = get_data(plug.msg, "start")
    bot.send_message(plug.chat_id, text.format(user=plug.msg.from_user.username), reply_markup=markup,
                     parse_mode="HTML")