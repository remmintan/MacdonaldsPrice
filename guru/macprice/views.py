# -*- coding: utf-8 -*-

import json
import logging
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from controllers.botmanager import FFPriceBot
from controllers import stats as st

class TelegramView(View):
    bot = FFPriceBot()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_info = logging.getLogger('django')
        self.log_error = logging.getLogger('django.request')

    def post(self, request, token):
        if not (token in self.bot.bots_dict):
            return HttpResponseForbidden('Invalid bot token')
        self.bot.set_bot(token)

        raw = request.body.decode('utf-8')
        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            try:
                self.bot.process_request(payload)
            except KeyError as e:
                text = 'KeyError in body: %s' % str(e)
                self.log_error.error(text)
                self.log_error.error(payload)

        response = JsonResponse({})
        response.status_code = 200
        return response

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TelegramView, self).dispatch(request, *args, **kwargs)


class StatsView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden('Access denied')

        last_login = request.user.last_login
        users = st.getChats()

        return render(request, 'macprice/index.html', {'last_login': last_login, 'users': users})