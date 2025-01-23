import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("aiogram.event").setLevel(logging.WARNING) # увеличивает минимальный уровень логов только для aiogram.event до WARNING, исключая INFO и DEBUG. Сделал, потому что в примере логи были без них
load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError('Переменная окружения BOT_TOKEN не установлена!')

WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
if not WEATHER_TOKEN:
    raise ValueError('Переменная окружения WEATHER_TOKEN не установлена!')