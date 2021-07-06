"""Telegram-бот. Уведомляет об измении статуса проверки домашней работы ЯП."""


import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

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
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'homework.log',
    mode='a',
    maxBytes=50_000_000,
    backupCount=5
)
logger.addHandler(handler)

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def send_message(message):
    """Отправляет сообщение в Telegram в указаный чат."""
    return bot.send_message(CHAT_ID, message)


def log_and_send_message(error, error_type, func_name):
    logger.error(error, exc_info=True)
    error_message = f'{error_type} {func_name}: {error}.'
    send_message(error_message)


def parse_homework_status(homework):
    """Генерирует варианты ответов для бота."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError as error:
        log_and_send_message(
            error,
            error_type='KeyError',
            func_name='in parse_homework_status'
        )
        return (
            'Variables "Homework_status" and/or ',
            '"homework_name" are not defined.'
        )
    else:
        if homework_status in HOMEWORK_STATUSES:
            verdict = HOMEWORK_STATUSES[homework_status]
        else:
            return log_and_send_message(
                error=f'status "{homework_status}" is unknown',
                error_type='Status is unknown',
                func_name='in parse_homework_status'
            )
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    """Опрашивает API Практикум.Домашка."""
    url = f'{PRAKTIKUM_API_URL}homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
        return homework_statuses.json()
    except requests.RequestException as error:
        log_and_send_message(
            error,
            error_type='RequestException',
            func_name='in get_homeworks'
        )
    except TypeError as error:
        log_and_send_message(
            error,
            error_type='TypeError',
            func_name='in get_homeworks'
        )
    except AttributeError as error:
        log_and_send_message(
            error,
            error_type='AttributeError',
            func_name='in get_homeworks'
        )


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
                log_and_send_message(
                    error='variable "api_answer" is not defined',
                    error_type='Variable is not defined',
                    func_name='in main'
                )
            time.sleep(SLEEP_LENGTH_FOR_WHILE)

        except Exception as error:
            log_and_send_message(
                error,
                error_type='Bot has crashed with error',
                func_name='in main'
            )
            time.sleep(SLEEP_LENGTH_WHEN_EXCEPTION)


if __name__ == '__main__':
    main()
