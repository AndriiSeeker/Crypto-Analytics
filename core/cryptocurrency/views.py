import csv
import time

from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import Crypto, News
from .utils.crypto_rate.rates import update_coins, write_to_file, get_date_rates
from .utils.crypto_news.news import update_news_info, get_date_news
from users.models import Profile, Watchlist


def filter_data(request):
    if 'watchlist' in request.path:
        favorites = request.user.watchlist.favorites
        crypto = Crypto.objects.filter(id__in=favorites)
    elif 'load_all' in request.path:
        crypto = Crypto.objects.all()[:15]
    else:
        crypto = Crypto.objects.all()
    return crypto


def user_data(request):
    avatar = ''
    favorites = []
    if request.user.is_authenticated:
        avatar = user_avatar(request)
        favorites = request.user.watchlist.favorites

        if request.method == 'POST':
            coin_id = int(request.POST.get('coin_id'))

            user = request.user
            user_watchlist = user.watchlist

            if coin_id in user_watchlist.favorites:
                # Coin is already in favorites, remove it
                user_watchlist.favorites.remove(coin_id)
                status = 'removed'
            else:
                # Coin is not in favorites, add it
                user_watchlist.favorites.append(coin_id)
                status = 'added'

            # Save the updated watchlist
            user_watchlist.save()
            favorites = user_watchlist.favorites
    return avatar, favorites


def user_dropdown(request):
    if request.method == 'POST':
        selected_option = request.POST.get('user_dropdown')

        if selected_option == 'profile':
            # Perform the action for viewing the profile
            return redirect(to="users:profile")
        elif selected_option == 'logout':
            logout(request)
            return redirect(to='cryptocurrency:home')

    return render(request, 'dropdown_template.html')


def user_avatar(request):
    profile = Profile.objects.get(user=request.user.id)
    avatar_url = profile.avatar
    return avatar_url


'''Home'''


def home(request):
    bitcoin = Crypto.objects.filter(coin_id=1)
    ethereum = Crypto.objects.filter(coin_id=1027)
    new = News.objects.all()[0]

    if request.user.is_authenticated:
        avatar = user_avatar(request)
    else:
        avatar = ''
    return render(request, 'cryptocurrency/home.html',
                  context={'bitcoin': bitcoin[0], 'ethereum': ethereum[0], 'news': new, 'avatar': avatar})


'''Crypto Rates'''


def rates(request):
    query_results = Crypto.objects.all().order_by('id')[:15]
    last_updated = get_date_rates()
    avatar, favorites = user_data(request)

    return render(request, 'cryptocurrency/crypto_rates.html',
                  context={'coins': query_results, 'date': last_updated, 'avatar': avatar, 'favorites': favorites})


'''Load More Crypto Rates'''


def load_more(request):
    query_results = Crypto.objects.all().order_by('id')
    last_updated = get_date_rates()

    avatar, favorites = user_data(request)

    return render(request, 'cryptocurrency/crypto_rates.html',
                  context={'coins': query_results, 'date': last_updated, 'avatar': avatar, 'favorites': favorites})


'''Update Rates'''


def update_rates(request):
    try:
        coins, last_updated = update_coins()
        time.sleep(1)
        for coin in coins:
            if Crypto.objects.filter(coin_id=coin[0]):
                Crypto.objects.filter(coin_id=coin[0]).update(
                    coin_id=coin[0],
                    name=coin[1],
                    symbol=coin[2],
                    price=coin[3],
                    percent_change_1h=coin[4],
                    percent_change_24h=coin[5],
                    percent_change_7d=coin[6],
                    circulating_supply=coin[7]
                )
            else:
                # Get the maximum id value from the Crypto table
                max_id = Crypto.objects.aggregate(Max('id'))['id__max']

                # Calculate the new id value by incrementing the maximum id
                new_id = max_id + 1 if max_id is not None else 1
                print(new_id)
                Crypto.objects.create(
                    id=new_id,
                    coin_id=coin[0],
                    name=coin[1],
                    symbol=coin[2],
                    price=coin[3],
                    percent_change_1h=coin[4],
                    percent_change_24h=coin[5],
                    percent_change_7d=coin[6],
                    circulating_supply=coin[7]
                )
                print('created')
        return redirect(to='cryptocurrency:rates')
    except IntegrityError as err:
        print(err)
        return render(request, "back_to_rates.html")


'''Download csv File'''


def download_file(request):
    data = Crypto.objects.all().order_by('id')
    if not data:
        data = ''
    headers = ["#", "coin_id", "name", "symbol", "price", "percent_change_1h", "percent_change_24h",
               "percent_change_7d", "circulating_supply"]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="coins.csv"'

    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(
        [coin.id, coin.coin_id, coin.name, coin.symbol, coin.price, coin.percent_change_1h, coin.percent_change_24h,
         coin.percent_change_7d, coin.circulating_supply] for coin in data
    )

    return response


'''Download csv File Authorized'''


def download_file_watchlist(request):
    favorites = request.user.watchlist.favorites
    data = Crypto.objects.filter(id__in=favorites).order_by('id')
    print(data)
    if not data:
        data = ''
    headers = ["#", "coin_id", "name", "symbol", "price", "percent_change_1h", "percent_change_24h",
               "percent_change_7d", "circulating_supply"]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="coins.csv"'

    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(
        [coin.id, coin.coin_id, coin.name, coin.symbol, coin.price, coin.percent_change_1h, coin.percent_change_24h,
         coin.percent_change_7d, coin.circulating_supply] for coin in data
    )

    return response


'''News'''


def news(request):
    query_results = News.objects.all()
    last_updated = get_date_news()
    per_page = 5
    paginator = Paginator(query_results, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.user.is_authenticated:
        avatar = user_avatar(request)
    else:
        avatar = ''
    return render(request, 'cryptocurrency/crypto_news.html',
                  context={'news_obj': page_obj, 'date': last_updated, 'avatar': avatar})


'''Update News'''


def update_news(request):
    crypro_news = update_news_info()
    time.sleep(1)
    News.objects.all().delete()
    for new in crypro_news:
        News.objects.create(
            title=new[0],
            text=new[1],
            date=new[2],
            source=new[3],
            link=new[4]
        )
    return redirect(to='cryptocurrency:news')


'''User Watchlist'''


def watchlist(request):
    if request.user.is_authenticated:
        avatar = user_avatar(request)
    else:
        avatar = ''

    favorites = []
    if request.user.is_authenticated:
        favorites = request.user.watchlist.favorites

    if favorites:
        query_results = Crypto.objects.filter(id__in=favorites).order_by('id')

        if request.method == 'POST':
            coin_id = int(request.POST.get('coin_id'))

            user = request.user
            user_watchlist = user.watchlist

            if coin_id in user_watchlist.favorites:
                # Coin is already in favorites, remove it
                user_watchlist.favorites.remove(coin_id)
                status = 'removed'
            else:
                # Coin is not in favorites, add it
                user_watchlist.favorites.append(coin_id)
                status = 'added'

            # Save the updated watchlist
            user_watchlist.save()
            favorites = user_watchlist.favorites
            query_results = Crypto.objects.filter(id__in=favorites).order_by('id')

        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'avatar': avatar,
                               'favorites': favorites})
    else:
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'avatar': avatar, 'favorites': favorites})


'''User By Coin Name'''


def search_field(request):
    request_query = request.GET.get('query').title()

    coins = Crypto.objects.filter(name__startswith=request_query).order_by('id')
    if not coins:
        coins = ''
    # favorites = request.user.watchlist.favorites
    # avatar = user_avatar(request)
    avatar, favorites = user_data(request)
    context = {
        'coins': coins,
        'avatar': avatar,
        'favorites': favorites,
        'request_query': request_query,
    }
    return render(request, "cryptocurrency/search_result.html", context=context)


'''Error 403'''


def handler403(request, exception):
    return render(request, 'cryptocurrency/page-403.html', status=403)


'''Error 404'''


def handler404(request, exception):
    return render(request, 'cryptocurrency/page-404.html', status=404)


'''Error 500'''


def handler500(request):
    return render(request, 'cryptocurrency/page-500.html', status=500)


'''Coins Filter'''


class Filter:
    last_updated = get_date_rates()

    @staticmethod
    def filter_by_price_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-price')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_price_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('price')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change1h_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-percent_change_1h')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change1h_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('percent_change_1h')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change24h_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-percent_change_24h')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change24h_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('percent_change_24h')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change7d_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-percent_change_7d')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change7d_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('percent_change_7d')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_supply_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-circulating_supply')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_supply_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('circulating_supply')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_id_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('id')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_id_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-id')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_name_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('name')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_name_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-name')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_symbol_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('symbol')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_symbol_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-symbol')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_coin_id_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('coin_id')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_coin_id_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-coin_id')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})


'''Coins Filter Authorized'''


class FilterWatchlist:
    last_updated = get_date_rates()

    @staticmethod
    def filter_by_price_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-price')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_price_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('price')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change1h_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-percent_change_1h')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change1h_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('percent_change_1h')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change24h_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-percent_change_24h')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change24h_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('percent_change_24h')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change7d_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-percent_change_7d')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_change7d_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('percent_change_7d')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_supply_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-circulating_supply')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_supply_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('circulating_supply')
        avatar, favorites = user_data(request)

        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_id_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('id')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_id_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-id')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_name_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('name')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_name_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-name')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_symbol_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('symbol')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_symbol_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-symbol')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_coin_id_descend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('coin_id')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})

    @staticmethod
    def filter_by_coin_id_ascend(request):
        crypto = filter_data(request)
        query_results = crypto.order_by('-coin_id')
        avatar, favorites = user_data(request)
        return render(request, 'cryptocurrency/watchlist.html',
                      context={'coins': query_results, 'date': Filter.last_updated, 'avatar': avatar,
                               'favorites': favorites})
