from modules.plugins import CommandPlugin
from modules.logging import logger
from modules import bot

def main(plug: CommandPlugin):
    bot.send_message(plug.chat_id, "HelloWorld")
    logger.debug(f"chat_id: {plug.chat_id} message: {plug.msg.text}")