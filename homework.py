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
SLEEP_LENGTH = 5 * 60


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
    maxBytes=50000000,
    backupCount=5
)
logger.addHandler(handler)

# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def parse_homework_status(homework):
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except TypeError as error:
        logger.error(error, exc_info=True)
        error_message = f'TypeError in parse_homework_status: {error}'
        send_message(error_message)
    except KeyError as error:
        logger.error(error, exc_info=True)
        error_message = f'KeyError in parse_homework_status: {error}'
        send_message(error_message)
    if homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif homework_status == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    else:
        verdict = (
            'Упс, ошибочка вышла. Вашу работу еще не проверили. ',
            'Но ее уже взяли в ревью, так что скоро проверят. ',
        )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
    except requests.RequestException as error:
        logger.error(error, exc_info=True)
        error_message = f'RequestException in get_homeworks: {error}'
        send_message(error_message)
    try:
        return homework_statuses.json()
    except TypeError as error:
        logger.error(error, exc_info=True)
        error_message = f'TypeError in get_homeworks: {error}'
        send_message(error_message)
    except ValueError as error:
        logger.error(error, exc_info=True)
        error_message = f'ValueError in get_homeworks: {error}'
        send_message(error_message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp
    time_before_sleep = current_timestamp - SLEEP_LENGTH

    while True:
        logger.debug('Bot has been started.')
        try:
            homeworks_from_api_answer = (
                get_homeworks(time_before_sleep)['homeworks']
            )
            if len(homeworks_from_api_answer) > 0:
                current_homework = homeworks_from_api_answer[0]
                message = parse_homework_status(current_homework)
                send_message(message)
                logger.info('Message has been sent.')
            time.sleep(SLEEP_LENGTH)  # Опрашивать раз в пять минут

        except Exception as error:
            logger.error(error, exc_info=True)
            error_message = f'Бот упал с ошибкой: {error}'
            send_message(error_message)
            time.sleep(5)


if __name__ == '__main__':
    main()
