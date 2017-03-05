# -*- coding: utf-8 -*-

import json
import logging
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from macprice.botmanager import FFPriceBot

# Create your views here.
botsDict = {
    "309603787:AAHB6uOEc9aRuQfUoYrjW_we4zF8LJIu82g": FFPriceBot("309603787:AAHB6uOEc9aRuQfUoYrjW_we4zF8LJIu82g"),
    # prodaction
    "279023466:AAHmCU7BcKcrR32Sw97esrCfa7C0oDykz9M": FFPriceBot("279023466:AAHmCU7BcKcrR32Sw97esrCfa7C0oDykz9M"),
    # development
}


class TelegramView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log = logging.getLogger('django')

    def post(self, request, token):
        if not (token in botsDict.keys()):
            return HttpResponseForbidden('Invalid bot token')
        activeBot = botsDict[token]

        raw = request.body.decode('utf-8')
        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            try:
                activeBot.processRequest(payload)
            except KeyError as e:
                text = 'KeyError in body: %s' % str(e)
                self.log.error(text)
                self.log.error(payload)

        response = JsonResponse({})
        response.status_code = 200
        return response

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TelegramView, self).dispatch(request, *args, **kwargs)
