import logging
import os

import telegram
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot_t = telegram.Bot(token=TELEGRAM_TOKEN)


class TelegramLogsHandler(logging.Handler):
    """Логи в чатик."""

    def __init__(self, telegram_chat_id):
        """Init."""
        super().__init__()
        self.chat_id = telegram_chat_id
        self.bot = telegram.Bot(token=TELEGRAM_TOKEN)

    def emit(self, record):
        """Emit."""
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)
