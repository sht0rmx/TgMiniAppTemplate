import asyncio
import logging
import os

from aiogram import Bot
from aiogram import Dispatcher
from dotenv import load_dotenv

from commands.handlers import router
from commands.queue_manager import start_worker
from db import database

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
