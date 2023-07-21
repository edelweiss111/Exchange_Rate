import telebot
import json
import os
from datetime import datetime

import requests

CURRENCY = ["USD", "EUR"]
API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')
RATES_FILE = 'currency.json'
API_BOT = os.getenv('TELEGRAM_BOT_RATE_API')


def main():
    """
    Основной код программы, который выводит курс валюты к рублю и сохраняет данные в файл
    """

    # Обращаемся к боту
    bot = telebot.TeleBot(API_BOT)

    # Вывод пользователю после команды "start"
    @bot.message_handler(commands=['start'])
    def starting(message):
        markup1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        eur = telebot.types.KeyboardButton('EUR')
        stop = telebot.types.KeyboardButton('/stop')
        markup1.add(eur, stop)
        mess = f'Привет {message.from_user.first_name}. ' \
               f'Введите название валюты трехбуквенным кодом (временно только "EUR")'
        bot.send_message(message.chat.id, mess, reply_markup=markup1)

    @bot.message_handler(commands=['stop'])
    def stopping(message):
        markup2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        start = telebot.types.KeyboardButton('/start')
        markup2.add(start)
        bot.send_message(message.chat.id, 'Бот остановлен', reply_markup=markup2)

    # Обрабатываем ввод пользователя
    @bot.message_handler(content_types=['text'])
    def get_user_text(message):
        # Если пользователь неправильно ввел валюту
        if message.text.upper() not in CURRENCY:
            bot.send_message(message.chat.id, 'Некоректный ввод, попробуйте снова')
        # Если пользователь правильно ввел валюту
        else:
            # Сохраняем курс в переменную
            rate = get_currency_rate(message.text)
            # Сохраняем дату и время запроса
            time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            # Выводим сообщение пользователю
            bot.send_message(message.chat.id, f'Курс {message.text.upper()} к рублю {round(rate, 2)}')

            # Сохраняем данные в файл
            data = {"currency": message.text, "rate": rate, "time": time, 'user': message.from_user.first_name}
            load_to_json(data)

            bot.send_message(message.chat.id, 'Выберете валюту')

    bot.polling(none_stop=True)


def get_currency_rate(currency):
    """
    Получает курс валюты от API и возвращает его в виде float
    """

    url = f"http://api.exchangeratesapi.io/v1/latest"
    response = requests.get(url, params={'access_key': API_KEY, 'base': currency})
    rate = response.json()['rates']['RUB']
    return rate


def load_to_json(data):
    """
    Сохраняет данные в json файл
    """
    with open(RATES_FILE, 'a') as file:
        if os.stat(RATES_FILE).st_size == 0:
            json.dump([data], file)
        else:
            with open(RATES_FILE) as json_file:
                data_list = json.load(json_file)
            data_list.append(data)
            with open(RATES_FILE, 'w') as json_file:
                json.dump(data_list, json_file)
