from telebot import TeleBot
from decouple import config

bot = TeleBot(str(config('TOKEN')))