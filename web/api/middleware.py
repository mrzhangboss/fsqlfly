# -*- coding:utf-8 -*-
from typing import Optional
from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest, HttpResponse, JsonResponse


def get_client_ip(request: HttpRequest) -> Optional[str]:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class LoginCheckMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if (not request.user.id) and (get_client_ip(request) not in ('127.0.0.1', 'localhost')):
            if (not request.path.startswith('/admin')) and (not request.path == '/'):
                return JsonResponse(data=dict(code=500, msg='need login', data=None))
        # Continue processing the request as usual:
        return self.get_response(request)
