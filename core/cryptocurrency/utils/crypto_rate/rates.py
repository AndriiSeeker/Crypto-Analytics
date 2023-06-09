import csv
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import environ
import requests

from .logger import get_logger

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

logger = get_logger(__name__)

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': env('API_KEY_RATE'),
}

absolute_path = os.path.dirname(__file__)

file_path_coins = Path(absolute_path + r"/data/coins.csv")
file_path_date = Path(absolute_path + r"/data/rates_update.txt")


def write_to_file(coins: list):
    try:
        with open(file_path_coins, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["#", "coin_id", "name", "symbol", "price", "percent_change_1h", "percent_change_24h",
                             "percent_change_7d", "circulating_supply"])
            for coin in coins:
                writer.writerow([coin.id, coin.coin_id, coin.name, coin.symbol, coin.price, coin.percent_change_1h,
                                 coin.percent_change_24h, coin.percent_change_7d, coin.circulating_supply])
    except Exception as err:
        logger.error(f'[ERROR] {err}')


def write_date_to_file(date):
    with open(file_path_date, 'w', newline='', encoding="utf-8") as file:
        file.write(str(date))


def get_date_rates():
    with open(file_path_date, 'r', encoding="utf-8") as file:
        date = file.read()
    return date


def convert_date(full_date):
    date_ = full_date.replace('T', ' ').replace('Z', '')
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    correct_date = datetime.strptime(date_, date_format) + timedelta(hours=3)
    return correct_date


def correct_num(num, symbols):
    num = float(num)
    num = round(num, symbols)
    num = format(num, f".{symbols}f")
    return num


def get_info(currency_conversion):
    try:
        parameters = {
            'start': '1',
            'limit': '800',
            'convert': currency_conversion
        }
        json = requests.get(url, params=parameters, headers=headers).json()
        coins_data = json['data']
        coins = []
        for coin in coins_data:
            try:
                '''data: {name, symbol, quote{"USD": {price, percent_change_1h, percent_change_24h, percent_change_7d}}, 
                circulating_supply, last_updated}'''

                id = coin['id']
                name = coin['name']
                symbol = coin['symbol']
                price = coin['quote'][currency_conversion]['price']
                price = correct_num(price, 2)

                percent_change_1h = coin['quote'][currency_conversion]['percent_change_1h']
                percent_change_1h = correct_num(percent_change_1h, 4)

                percent_change_24h = coin['quote'][currency_conversion]['percent_change_24h']
                percent_change_24h = correct_num(percent_change_24h, 4)

                percent_change_7d = coin['quote'][currency_conversion]['percent_change_7d']
                percent_change_7d = correct_num(percent_change_7d, 4)

                circulating_supply = round(coin['circulating_supply'])
                last_updated = convert_date(coin['last_updated'])

                if name and symbol and price and percent_change_1h and percent_change_24h and percent_change_7d and \
                        circulating_supply and last_updated:
                    coins.append([id, name, symbol, price, percent_change_1h, percent_change_24h,
                                  percent_change_7d, circulating_supply])

            except Exception as error:
                logger.error(f'[ERROR] {error}')

        if coins and last_updated:
            write_date_to_file(last_updated)
            return coins, last_updated
            # write_to_file(coins, last_updated)

    except requests.exceptions.RequestException as error:
        logger.error(f'[ERROR] {error}')


def update_coins(currency_conversion="USD"):
    logger.log(level=logging.DEBUG, msg=f"Start")
    coins, last_updated = get_info(currency_conversion)
    logger.log(level=logging.DEBUG, msg=f"End")
    return coins, last_updated
