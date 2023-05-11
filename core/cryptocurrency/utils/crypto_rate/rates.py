import csv
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests

from .config import API_KEY
from .logger import get_logger

logger = get_logger(__name__)

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
}

absolute_path = os.path.dirname(__file__)
file_path_coins = Path(absolute_path + r"\data\coins.csv")
file_path_date = Path(absolute_path + r"\data\rates_update.txt")


def write_to_file(coins: list, date: datetime):
    try:
        with open(file_path_date, 'w', newline='', encoding="utf-8") as file:
            file.write(str(date))

        with open(file_path_coins, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["#", "name", "symbol", "price", "percent_change_1h", "percent_change_24h",
                             "percent_change_7d", "circulating_supply"])
            for coin in coins:
                writer.writerow([elem for elem in coin])
    except Exception as err:
        logger.error(f'[ERROR] {err}')


def convert_date(full_date):
    date_ = full_date.replace('T', ' ').replace('Z', '')
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    correct_date = datetime.strptime(date_, date_format) + timedelta(hours=3)
    return correct_date


def get_info(currency_conversion):
    try:
        parameters = {
            'start': '1',
            'limit': '100',
            'convert': currency_conversion
        }
        json = requests.get(url, params=parameters, headers=headers).json()
        coins_data = json['data']
        coins = []
        counter = 1
        for coin in coins_data:
            try:
                '''data: {name, symbol, quote{"USD": {price, percent_change_1h, percent_change_24h, percent_change_7d}}, 
                circulating_supply, last_updated}'''

                name = coin['name']
                symbol = coin['symbol']
                price = round(coin['quote']['EUR']['price'], 2)
                percent_change_1h = round(coin['quote']['EUR']['percent_change_1h'], 4)
                percent_change_24h = round(coin['quote']['EUR']['percent_change_24h'], 4)
                percent_change_7d = round(coin['quote']['EUR']['percent_change_7d'], 4)
                circulating_supply = round(coin['circulating_supply'])
                last_updated = convert_date(coin['last_updated'])
                if name and symbol and price and percent_change_1h and percent_change_24h and percent_change_7d and\
                        circulating_supply and last_updated:
                    coins.append([counter, name, symbol, price, percent_change_1h, percent_change_24h,
                                  percent_change_7d, circulating_supply])
                    counter += 1
            except Exception as error:
                logger.error(f'[ERROR] {error}')

        if coins and last_updated:
            write_to_file(coins, last_updated)

    except requests.exceptions.RequestException as error:
        logger.error(f'[ERROR] {error}')


def update_coins(currency_conversion="USD"):
    logger.log(level=logging.DEBUG, msg=f"Start")
    get_info(currency_conversion)
    logger.log(level=logging.DEBUG, msg=f"End")
