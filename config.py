import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
aiohttp_logger = logging.getLogger("aiohttp")
aiohttp_logger.setLevel(logging.DEBUG)
load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError('Переменная окружения BOT_TOKEN не установлена!')

WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
if not WEATHER_TOKEN:
    raise ValueError('Переменная окружения WEATHER_TOKEN не установлена!')