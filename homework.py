from http import HTTPStatus
import logging
import os
import time
import requests
import telegram
import json
import datetime



from dotenv import load_dotenv
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

CURRENT_TIMESTAMP = int(datetime.datetime(2021, 1, 1, 0, 0).timestamp())


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='ya_bot.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(
    logging.StreamHandler()
)


class RequestError(Exception):
    """Request Error."""


def send_message(bot, message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение отправленно: {message}')
    except telegram.TelegramError as error:
        logger.error(f'Сообщение не отправленно: {error}')


def get_api_answer(current_timestamp):
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            api_answer = (f'ENDPOINT {ENDPOINT} недоступен.',
                          f'Код ответа: {response.status_code}')
            logger.error(api_answer)
            raise requests.HTTPError(api_answer)
        return response.json()
    except requests.exceptions.RequestException as requests_error:
        api_answer = f'Код ответа: {requests_error}'
        logger.error(api_answer)
        raise RequestError(api_answer)
    except json.JSONDecoder as value_error:
        api_answer = f'Код ответа: {value_error}'
        logger.error(api_answer)
        raise json.JSONDecodeError(api_answer)


def check_response(response):
    if not isinstance(response, dict):
        api_message = 'Ожидался словарь.'
        logger.error(api_message)
        raise TypeError(api_message)
    if len(response) == 0:
        api_message = 'Пустой словарь'
        logger.error(api_message)
        raise Exception(api_message)
    if 'homeworks' not in response.keys():
        api_message = 'Отсутсвует ключ в словаре'
        logger.error(api_message)
        raise Exception(api_message)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise Exception('Ошибка данных')
    return homeworks


def parse_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None:
        api_message = 'Пустое значение homework_name'
        logger.error(api_message)
        raise KeyError(api_message)
    if homework_status not in HOMEWORK_STATUSES.keys():
        api_message = 'Неверный статус работы'
        logger.error(api_message)
        raise KeyError(api_message)

    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    if TELEGRAM_TOKEN and PRACTICUM_TOKEN and TELEGRAM_CHAT_ID is not None:
        return True


def main():
    """Основная логика работы бота."""
    homework_status = 'Неизвестный статус'
    errors = None
    if check_tokens() is not True:
        exit()
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
                    logger.info('Изменений нет')

        except Exception as error:
            if error != errors:
                message = f'Сбой в работе бота: {error}'
                send_message(bot, message)
                errors = error
            time.sleep(RETRY_TIME)
        else:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()