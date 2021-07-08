"""Telegram-бот. Уведомляет об измении статуса проверки домашней работы ЯП."""


import logging
import os
import time
from json.decoder import JSONDecodeError
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv
from telegram_handler import TelegramHandler

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRAKTIKUM_API_URL = 'https://praktikum.yandex.ru/api/user_api/'
HOMEWORK_STATUSES = {
    'rejected': 'К сожалению, в работе нашлись ошибки.',
    'approved': 'Ревьюеру всё понравилось, работа зачтена!',
    'reviewing': (
        'Упс, ошибочка вышла. Вашу работу еще не проверили. ',
        'Но ее уже взяли в ревью, так что скоро проверят. '
    ),
}
SLEEP_LENGTH_FOR_WHILE = 5 * 60
SLEEP_LENGTH_WHEN_EXCEPTION = 30

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='a',
    format='%(asctime)s, %(levelname)s, %(funcName)s, %(message)s, %(name)s',
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_format = logging.Formatter(
    '%(asctime)s,'
    '%(levelname)s,'
    '%(funcName)s,'
    '%(message)s,'
    '%(name)s'
)
file_handler = RotatingFileHandler(
    'homework.log',
    mode='a',
    maxBytes=50_000_000,
    backupCount=5
)
file_handler.setFormatter(log_format)
tg_handler = TelegramHandler(
    token=TELEGRAM_TOKEN,
    chat_id=CHAT_ID,
)
tg_handler.setLevel(logging.ERROR)
tg_handler.setFormatter(log_format)

logger.addHandler(file_handler)
logger.addHandler(tg_handler)


bot = telegram.Bot(token=TELEGRAM_TOKEN)


def send_message(message):
    """Отправляет сообщения в Telegram."""
    return bot.send_message(CHAT_ID, message)


def parse_homework_status(homework):
    """Генерирует варианты ответов для бота."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError as error:
        logger.error(f'{error.__class__.__name__}: {error}.', exc_info=True)
        return (
            'Variables "Homework_status" and/or ',
            '"homework_name" are not defined.'
        )
    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    else:
        return logger.error(
            f'Status "{homework_status}" is unknown.',
            exc_info=True
        )


def get_homeworks(current_timestamp):
    """Опрашивает API Практикум.Домашка."""
    url = f'{PRAKTIKUM_API_URL}homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
        return homework_statuses.json()
    except (requests.RequestException, TypeError, JSONDecodeError) as error:
        logger.error(f'{error.__class__.__name__}: {error}.', exc_info=True)


def main():
    """Задает цикл работы бота."""
    current_timestamp = int(time.time())

    while True:
        logger.debug('Bot has been started.')
        try:
            api_answer = get_homeworks(current_timestamp)
            if api_answer:
                homeworks_from_api_answer = (
                    api_answer['homeworks']
                )
                current_timestamp = api_answer['current_date']
                if homeworks_from_api_answer:
                    current_homework = homeworks_from_api_answer[0]
                    message = parse_homework_status(current_homework)
                    send_message(message)
                    logger.info('Message has been sent.')
            else:
                logger.error(
                    'No response from the server has received. ',
                    exc_info=True
                )
            time.sleep(SLEEP_LENGTH_FOR_WHILE)

        except Exception as error:
            logger.error(
                f'{error.__class__.__name__}: {error}.',
                exc_info=True
            )
            time.sleep(SLEEP_LENGTH_WHEN_EXCEPTION)


if __name__ == '__main__':
    main()
