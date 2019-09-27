"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import path, include, re_path
from .settings import BASE_DIR
import magic

base_picture_dir = os.path.join(BASE_DIR, 'upload', 'logo')
FileMagic = magic.Magic(mime=True, uncompress=True)


def get_picture(req: HttpRequest, name: str) -> HttpResponse:
    full_path = os.path.join(base_picture_dir, name)
    mime = FileMagic.from_file(full_path)
    image_data = open(full_path, "rb").read()
    return HttpResponse(image_data, content_type=mime)


def to_static(*args, **kwargs) -> HttpResponse:
    return redirect('/static/index.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('upload/logo/<str:name>', get_picture),
    re_path('(resouces|transform)/.*', to_static),
]
