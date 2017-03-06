# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^stats/$', views.StatsView.as_view()),
    url(r'^(?P<token>.+)/$', views.TelegramView.as_view()),
]
