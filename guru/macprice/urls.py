# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.StatsView.as_view()),
    url(r'^(?P<token>.+)/$', views.TelegramView.as_view()),
]
