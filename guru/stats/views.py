from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.views import View

from stats import controllers as cont


# Create your views here.
class IndexView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden('Access denied')

        last_login = request.user.last_login
        users = cont.getChats()

        return render(request, 'stats/index.html', {'last_login': last_login, 'users': users})
