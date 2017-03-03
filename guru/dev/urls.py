# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^(?P<rest>[a-z]+)/(?P<sum>[0-9]+)/$', views.DevView.as_view(), name='order'),
    url(r'^(?P<rest>[a-z]+)/(?P<name>.+)/$', views.GroupView.as_view(), name='group'),

]
