from configparser import ConfigParser

from aiogram import Bot

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

config = ConfigParser()
config.read('config.ini')

DATABASE = config['DATABASE']['NAME']
TG_TOKEN = config['TELEGRAM']['TOKEN']

bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
