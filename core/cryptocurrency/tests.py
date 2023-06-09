class CryptoRates:
    def __init__(self, query_results):
        self.query_results = query_results

    '''Crypto Rates'''

    def rates(self, request):
        self.query_results = Crypto.objects.all().order_by('id')[:15]
        last_updated = get_date_rates()
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

                return render(request, 'cryptocurrency/crypto_rates.html',
                              context={'coins': query_results, 'date': last_updated, 'avatar': avatar,
                                       'favorites': favorites, 'status': status})

        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': self.query_results, 'date': last_updated, 'avatar': avatar, 'favorites': favorites})

    '''Load More Crypto Rates'''

    def load_more(self, request):
        self.query_results = Crypto.objects.all()
        last_updated = get_date_rates()
        if request.user.is_authenticated:
            avatar = user_avatar(request)
        else:
            avatar = ''
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': self.query_results, 'date': last_updated, 'avatar': avatar})

    '''Update Rates'''

    def update_rates(self, request):
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
                Crypto.objects.create(
                    coin_id=coin[0],
                    name=coin[1],
                    symbol=coin[2],
                    price=coin[3],
                    percent_change_1h=coin[4],
                    percent_change_24h=coin[5],
                    percent_change_7d=coin[6],
                    circulating_supply=coin[7]
                )

        self.query_results = Crypto.objects.all()[:15]
        if request.user.is_authenticated:
            avatar = user_avatar(request)
        else:
            avatar = ''
        return render(request, 'cryptocurrency/crypto_rates.html',
                      context={'coins': self.query_results, 'date': last_updated, 'avatar': avatar})

    '''Download csv File'''

    def download_file(self, request):
        print(self.query_results)

    '''User Watchlist'''

    def watchlist(self, request):
        if request.user.is_authenticated:
            avatar = user_avatar(request)
        else:
            avatar = ''

        favorites = []
        if request.user.is_authenticated:
            favorites = request.user.watchlist.favorites

        if favorites:
            self.query_results = Crypto.objects.filter(id__in=favorites).order_by('id')

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
                self.query_results = Crypto.objects.filter(id__in=favorites).order_by('id')

            return render(request, 'cryptocurrency/watchlist.html',
                          context={'coins': self.query_results, 'avatar': avatar,
                                   'favorites': favorites})
        else:
            return render(request, 'cryptocurrency/watchlist.html',
                          context={'avatar': avatar, 'favorites': favorites})

    '''User By Coin Name'''

    def search_field(self, request):
        request_query = request.POST.get('query').title()
        if request.user.is_authenticated:
            avatar = user_avatar(request)
        else:
            avatar = ''

        self.query_results = Crypto.objects.filter(name__startswith=request_query).order_by('id')
        if not self.query_results:
            self.query_results = ''
        context = {
            'coins': self.query_results,
            'avatar': avatar,
        }
        return render(request, "cryptocurrency/crypto_rates.html", context=context)
