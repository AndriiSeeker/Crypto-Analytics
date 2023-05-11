from django.urls import path
from . import views

app_name = 'cryptocurrency'

urlpatterns = [
    path('', views.home, name='home'),
    path('rates/', views.rates, name='rates'),
    path('rates/load_more/', views.load_more, name='load_more'),
    path('rates/update/', views.update_rates, name='update_rates'),
    path('rates/download/', views.download_file, name='download'),
    path('news/', views.news, name='news'),
    path('news/<int:page>', views.news, name='root_paginate'),
    path('news/update/', views.update_news, name='update_news'),
]
