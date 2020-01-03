# -*- coding:utf-8 -*-
from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest, HttpResponse, JsonResponse


class LoginCheckMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not request.user.id:
            if (not request.path.startswith('/admin')) and (not request.path == '/'):
                return JsonResponse(data=dict(code=500, msg='need login', data=None))
        # Continue processing the request as usual:
        return self.get_response(request)
