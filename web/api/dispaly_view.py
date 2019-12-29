# -*- coding:utf-8 -*-
from django.http import HttpRequest, JsonResponse


def search(req: HttpRequest) -> JsonResponse:
    return JsonResponse({})
