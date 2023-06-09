from django.db import models


class Crypto(models.Model):
    coin_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    percent_change_1h = models.DecimalField(max_digits=10, decimal_places=4)
    percent_change_24h = models.DecimalField(max_digits=10, decimal_places=4)
    percent_change_7d = models.DecimalField(max_digits=10, decimal_places=4)
    circulating_supply = models.BigIntegerField()


class News(models.Model):
    title = models.TextField()
    text = models.TextField()
    date = models.CharField()
    source = models.CharField()
    link = models.TextField()
