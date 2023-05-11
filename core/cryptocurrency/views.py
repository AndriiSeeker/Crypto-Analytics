import time
import os
from pathlib import Path
from csv import DictReader

from django.core.paginator import Paginator
from django.http import FileResponse
from django.shortcuts import render

from .utils.crypto_rate.rates import update_coins
from .utils.crypto_news.news import update_news_info


absolute_path = os.path.dirname(__file__)


def get_coins():
    relative_path = r"utils\crypto_rate\data"
    path_to_data = os.path.join(absolute_path, relative_path)
    file_path_coins = Path(path_to_data + r"\coins.csv")
    file_path_date = Path(path_to_data + r"\rates_update.txt")

    coins = []
    with open(file_path_coins, 'r', encoding="utf8") as file:
        csv_reader = DictReader(file)
        for row in csv_reader:
            coins.append(row)

    with open(file_path_date, 'r', encoding="utf8") as file:
        date = file.read()
    return coins, date


def get_news():
    relative_path = r"utils\crypto_news\data"
    path_to_data = os.path.join(absolute_path, relative_path)
    file_path_news = Path(path_to_data + r"\news.csv")
    file_path_date = Path(path_to_data + r"\news_update.txt")

    crypro_news = []
    with open(file_path_news, 'r', encoding="utf8") as file:
        csv_reader = DictReader(file)
        for row in csv_reader:
            crypro_news.append(row)

    with open(file_path_date, 'r', encoding="utf8") as file:
        date = file.read()
    return crypro_news, date


'''VIEWS'''


# Home
def home(request):
    crypro_news, *_ = get_news()
    coins, *_ = get_coins()
    return render(request, 'cryptocurrency/home.html', context={'news': crypro_news[:2], 'coins': coins[:5]})


# Crypto Rates
def rates(request):
    coins, date = get_coins()
    return render(request, 'cryptocurrency/crypto_rates.html',
                  context={'coins': coins[:15], 'date': date})


# Load More Crypto Rates
def load_more(request):
    coins, date = get_coins()
    return render(request, 'cryptocurrency/crypto_rates.html', context={'coins': coins, 'date': date})


# Update Rates
def update_rates(request):
    update_coins()
    time.sleep(1)
    coins, date = get_coins()
    return render(request, 'cryptocurrency/crypto_rates.html', context={'coins': coins[:15], 'date': date})


# Download csv File
def download_file(request):
    filename = r'D:\programming\Python\CryptoAnalytics\core\cryptocurrency\utils\crypto_rate\data\coins.csv'
    response = FileResponse(open(filename, 'rb'))
    return response


# News
def news(request):
    crypro_news, date = get_news()
    per_page = 5
    paginator = Paginator(list(crypro_news), per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'cryptocurrency/crypto_news.html', context={'news': page_obj, 'date': date})


def update_news(request):
    update_news_info()
    time.sleep(1)
    crypro_news, date = get_news()
    return render(request, 'cryptocurrency/crypto_news.html', context={'news': crypro_news[:5], 'date': date})
