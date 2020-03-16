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
from .views import create_or_get_list, update_or_delete, current_user, upload, count_view, run_model_command
from .transform_view import get_info, get_list_or_create, get_or_update_or_delete as transform_update_or_delete, \
    start_run, debug_transform, job_control_api, job_list, stop_run, restart_run
from .dispaly_view import search, list_tables, get_related_tables, list_table_names

urlpatterns = [
    path('currentUser', current_user),
    path('search/<str:table_name>', search),
    path('tables', list_tables),
    path('table_names', list_table_names),
    path('table/<str:table_name>', get_related_tables),
    path('count', count_view),
    path('transform', get_list_or_create),
    path('transform/debug/<int:pk>', debug_transform),
    path('transform/info', get_info),
    path('transform/<int:pk>', transform_update_or_delete),
    path('transform/run/<int:pk>', start_run),
    path('transform/stop/<int:pk>', stop_run),
    path('transform/restart/<int:pk>', restart_run),
    path('upload', upload),
    path('jobs/<str:name>/<str:mode>', job_control_api),
    path('jobs', job_list),
    path('<str:model>', create_or_get_list),
    path('<str:model>/<int:pk>', update_or_delete),
    path('<str:model>/<str:method>/<int:pk>', run_model_command),
]
