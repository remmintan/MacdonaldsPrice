# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
	url(ur'^(?P<rest>[a-z]+)/(?P<name>[а-яА-Я]+)/$', views.GroupView.as_view()),
	url(r'^(?P<rest>[a-z]+)/(?P<sum>[0-9]+)/$', views.DevView.as_view()),
	url(r'^(?P<token>.+)/$', views.TelegramView.as_view()),
]
