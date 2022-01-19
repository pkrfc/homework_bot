import logging
import os
import time
import json
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

CURRENT_TIMESTAMP = int(time.time())
BOT = telegram.Bot(token=TELEGRAM_TOKEN)

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


class TelegramLogsHandler(logging.Handler):
    """Логи в чатик."""

    def __init__(self, BOT, TELEGRAM_CHAT_ID):
        """Init."""
        super().__init__()
        self.chat_id = TELEGRAM_CHAT_ID
        self.bot = BOT

    def emit(self, record):
        """Emit."""
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


logging.basicConfig(
    level=logging.DEBUG,
    filename='ya_bot.log',
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(
    logging.StreamHandler()
)
logger.addHandler(TelegramLogsHandler(BOT, TELEGRAM_CHAT_ID))


class RequestError(Exception):
    """Request Error."""


class EmptyDict(Exception):
    """Пустой словарь."""


class ErrorKeyDict(Exception):
    """Отсутсвует ключ в словаре."""


class DataError(Exception):
    """Ошибка данных."""


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение отправленно: {message}')
    except telegram.TelegramError as error:
        logger.error(f'Сообщение не отправленно: {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            api_answer = (f'ENDPOINT {ENDPOINT} недоступен.',
                          f'Код ответа: {response.status_code}')
            logger.error(api_answer)
            raise requests.HTTPError(api_answer)
        return response.json()
    except requests.exceptions.ConnectTimeout as connect_error:
        api_answer = f'Код ответа: {connect_error}'
        logger.error(api_answer)
        raise RequestError(api_answer)
    except requests.exceptions.RequestException as requests_error:
        api_answer = f'Код ответа: {requests_error}'
        logger.error(api_answer)
        raise RequestError(api_answer)
    except json.JSONDecoder:
        api_answer = 'Не валидный json'
        logger.error(api_answer)
        raise json.JSONDecodeError(api_answer)


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        api_message = 'Ожидался словарь.'
        logger.error(api_message)
        raise TypeError(api_message)
    if not response:
        api_message = 'Пустой словарь'
        logger.error(api_message)
        raise EmptyDict(api_message)
    if 'homeworks' not in response:
        api_message = 'Отсутсвует ключ в словаре'
        logger.error(api_message)
        raise ErrorKeyDict(api_message)
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise DataError('Ошибка данных')
    return homeworks


def parse_status(homework):
    """Извлекает статус работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None:
        api_message = 'Пустое значение homework_name'
        logger.error(api_message)
        raise KeyError(api_message)
    if homework_status not in HOMEWORK_STATUSES:
        api_message = f'Неизвестный статус работы: {homework_status}'
        logger.error(api_message)
        raise KeyError(api_message)

    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    tokens = [TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID]
    for tkn in tokens:
        if tkn is None:
            logger.error('Не доступна переменная')
            return False
    return True


def main():
    """Основная логика работы бота."""
    homework_status = 'Неизвестный статус'
    previous_error = None
    if not check_tokens():
        exit(1)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            response = get_api_answer(CURRENT_TIMESTAMP)
            homeworks = check_response(response)
            if homeworks:
                last_homework = homeworks[0]
                status = parse_status(last_homework)
                if homework_status != status:
                    homework_status = status
                    send_message(bot, status)
                else:
                    logger.debug('Изменений нет')

        except Exception as error:
            if error != previous_error:
                message = f'Сбой в работе бота: {error}'
                send_message(bot, message)
                previous_error = error
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
