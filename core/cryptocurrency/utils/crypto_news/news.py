import csv
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests

from .config import API_KEY
from .logger import get_logger

logger = get_logger(__name__)

url = "https://crypto-news11.p.rapidapi.com/cryptonews/bitcoin"

querystring = {"max_articles": "15", "last_n_hours": "48", "top_n_keywords": "10"}

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "crypto-news11.p.rapidapi.com"
}

absolute_path = os.path.dirname(__file__)
file_path_news = Path(absolute_path + r"\data\news.csv")
file_path_date = Path(absolute_path + r"\data\news_update.txt")


def write_to_file(news: list, date: datetime):
    try:
        with open(file_path_date, 'w', newline='', encoding="utf-8") as file:
            file.write(str(date))

        with open(file_path_news, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["title", "text", "date", "source", "link"])
            for new in news:
                writer.writerow([elem for elem in new])
    except Exception as err:
        logger.error(f'[ERROR] {err}')


def get_info():
    try:
        json = requests.get(url, headers=headers, params=querystring).json()
        news_data = json.get('articles')
        news = []
        for new in news_data:
            try:
                '''title, text, date, source, link'''
                print(new)
                title = new.get('title')
                text = new.get('text')
                date = str(new.get('date'))
                source = new.get('source')
                link = new.get('url')
                if title and text and date and source and link:
                    news.append([title, text, date, source, link])

            except Exception as error:
                logger.error(f'[ERROR] {error}')

        last_updated = datetime.now().replace(microsecond=0)
        if news and last_updated:
            write_to_file(news, last_updated)

    except requests.exceptions.RequestException as error:
        logger.error(f'[ERROR] {error}')


def update_news_info():
    logger.log(level=logging.DEBUG, msg=f"Start")
    get_info()
    logger.log(level=logging.DEBUG, msg=f"End")

