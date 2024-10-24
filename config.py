from configparser import RawConfigParser

from aiogram import Bot

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

config = RawConfigParser()
config.read('config.ini')

DATABASE = config['DATABASE']['NAME']
TG_TOKEN = config['TELEGRAM']['TOKEN']

DONATION_URL = config['OTHER']['DONATION_URL']

SHIKI_CLIENT_ID = config['SHIKIMORI']['CLIENT_ID']
SHIKI_CLIENT_SECRET = config['SHIKIMORI']['CLIENT_SECRET']
SHIKI_OAUTH_URL = config['SHIKIMORI']['OAUTH_URL']

bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
