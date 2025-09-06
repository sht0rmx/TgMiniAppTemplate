import os

from telebot.types import Message, InlineQuery, CallbackQuery
from modules import bot

from modules.bot_funcs import bot_info

from modules.plugins import PluginManager, Plugin
from modules.logging import logger

plug_dir = os.path.join(os.getcwd(), 'plugins')
if not os.path.isdir(plug_dir):
    os.makedirs(plug_dir, exist_ok=True)
plugin_manager = PluginManager()

from modules.db import dbclient  # твой PocketBaseClient

@bot.message_handler(commands=None, func=lambda m: m.text and m.text.startswith('/'))
def _command(message: Message):
    dbclient.check_user(message)
    cmd = message.text.partition(' ')[0].partition('@')[0]
    for r in plugin_manager.find_command(cmd):
        p = Plugin.create('command')
        p.msg = message
        p.chat_id = message.chat.id
        p.user_id = message.from_user.id
        plugin_manager.run_handler(r, p)


@bot.callback_query_handler(func=lambda callback: True)
def _callback(callback: CallbackQuery):
    data = callback.data or ''
    for r in plugin_manager.find_callback(data):
        p = Plugin.create('callback')
        p.callback_args = data.split(':')
        p.callback_data = data
        p.cb = callback
        p.msg = callback.message
        p.chat_id = callback.message.chat.id if callback.message else None
        plugin_manager.run_handler(r, p)


@bot.inline_handler(func=lambda query: True)
def _inl(query: InlineQuery):
    fake_msg = type("Obj", (), {"chat": query.from_user, "from_user": query.from_user})()
    dbclient.check_user(fake_msg)

    txt = query.query or ''
    for r in plugin_manager.find_inline(txt):
        p = Plugin.create('inline')
        p.text = txt
        p.inline_data = query
        p.user_id = query.from_user.id
        plugin_manager.run_handler(r, p)


@bot.message_handler(func=lambda m: True, content_types=['text', 'voice', 'audio', 'photo', 'document'])
def _message(message: Message):
    dbclient.check_user(message)
    for r in plugin_manager.find_message_handler(message):
        p = Plugin.create('message')
        p.msg = message
        p.chat_id = message.chat.id
        p.user_id = message.from_user.id
        plugin_manager.run_handler(r, p)




if __name__ == '__main__':
    logger.info('Starting Bot')
    bot_info()
    bot.infinity_polling()
