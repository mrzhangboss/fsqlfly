"""stockmarket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from .views import create_or_get_list, update_or_delete, current_user, upload, count_view
from .transform_view import get_info, get_list_or_create, get_or_update_or_delete as transform_update_or_delete, start_run, debug_transform
urlpatterns = [
    path('currentUser', current_user),
    path('count', count_view),
    path('transform', get_list_or_create),
    path('transform/debug', debug_transform),
    path('transform/info', get_info),
    path('transform/<int:pk>', transform_update_or_delete),
    path('transform/<int:pk>/run', start_run),
    path('upload', upload),
    path('<str:model>', create_or_get_list),
    path('<str:model>/<int:pk>', update_or_delete),
]

