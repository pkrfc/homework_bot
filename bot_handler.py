import os

import telegram
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot_t = telegram.Bot(token=TELEGRAM_TOKEN)
