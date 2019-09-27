from django.contrib import admin

# Register your models here.

from dbs.models import Namespace, FileResource, Resource


# Register your models here.

@admin.register(Namespace, FileResource, Resource)
class StockAdmin(admin.ModelAdmin):
    pass
