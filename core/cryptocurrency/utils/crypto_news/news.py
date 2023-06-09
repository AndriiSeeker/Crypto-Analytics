import csv
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import environ
import requests
import unicodedata

from .logger import get_logger

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

logger = get_logger(__name__)

url = "https://crypto-news11.p.rapidapi.com/cryptonews/bitcoin"

querystring = {"max_articles": "15", "last_n_hours": "48", "top_n_keywords": "10"}

headers = {
    "X-RapidAPI-Key": env('API_KEY_NEWS'),
    "X-RapidAPI-Host": env('API_HOST_NEWS')
}

absolute_path = os.path.dirname(__file__)
file_path_news = Path(absolute_path + r"/data/news.csv")
file_path_date = Path(absolute_path + r"/data/news_update.txt")


# def write_to_file(news: list, date: datetime):
#     try:
#         with open(file_path_date, 'w', newline='', encoding="utf-8") as file:
#             file.write(str(date))
#
#         with open(file_path_news, 'w', newline='', encoding="utf-8") as file:
#             writer = csv.writer(file)
#             writer.writerow(["title", "text", "date", "source", "link"])
#             for new in news:
#                 writer.writerow([elem for elem in new])
#     except Exception as err:
#         logger.error(f'[ERROR] {err}')

def write_date_to_file(date):
    with open(file_path_date, 'w', newline='', encoding="utf-8") as file:
        file.write(str(date))


def get_date_news():
    with open(file_path_date, 'r', encoding="utf-8") as file:
        date = file.read()
    return date


def normalize_text(text: str):
    text = text.strip().replace(r'\x9', '').replace(r'\x0', '').replace(r'\ax0', '').replace(r'\xa0', '')
    new_text = unicodedata.normalize("NFKD", text)
    return new_text


def get_info():
    try:
        request = requests.get(url, headers=headers, params=querystring)
        json = request.json()
        news_data = json.get('articles')
        news = []
        for new in news_data:
            try:
                '''title, text, date, source, link'''
                title = new.get('title')
                title = normalize_text(title)

                text = new.get('text')
                text = normalize_text(text)

                date = str(new.get('date'))
                source = new.get('source')
                link = new.get('url')
                if title and text and date and source and link:
                    news.append([title, text, date, source, link])

            except Exception as error:
                logger.error(f'[ERROR] {error}')

        last_updated = datetime.now().replace(microsecond=0)
        if news and last_updated:
            write_date_to_file(last_updated)
            return news

    except requests.exceptions.RequestException as error:
        logger.error(f'[ERROR] {error}')


def update_news_info():
    try:
        logger.log(level=logging.DEBUG, msg=f"Start")
        news = get_info()
        logger.log(level=logging.DEBUG, msg=f"End")
        return news
    except Exception as err:
        logger.error(f'[ERROR] {err}')
