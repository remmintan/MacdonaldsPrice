from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^(?P<sum>\w+)/$', views.DevView.as_view()),
]
