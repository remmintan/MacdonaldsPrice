from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^(?P<sum>\d+)/$', views.DevView.as_view()),
]
