from django.contrib import admin

# Register your models here.

from dbs.models import Namespace, FileResource, Resource, Functions, Transform, Connection, Relationship


# Register your models here.

@admin.register(Namespace)
class NamespaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'info', 'image_tag', '_create_at', '_update_at']
    list_filter = ['is_publish', 'is_available', 'is_deleted']


@admin.register(FileResource)
class FileResourceAdmin(admin.ModelAdmin):
    search_fields = ['unique_name']
    list_display = ['unique_name', 'info', 'real_path', '_create_at', '_update_at']
    list_filter = ['is_publish', 'is_available', 'is_deleted']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['_name_space_name', 'name', 'info', 'typ', '_create_at', '_update_at']
    search_fields = ['name']
    list_filter = ['namespace', 'typ', 'is_publish', 'is_available', 'is_deleted']


@admin.register(Functions)
class FunctionsAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'function_from', 'class_name', '_create_at', '_update_at']
    list_filter = ['is_publish', 'is_available', 'is_deleted']


@admin.register(Transform)
class TransformAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'info', '_name_space_name', '_create_at', '_update_at']
    list_filter = ['namespace', 'is_publish', 'is_available', 'is_deleted']


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'info']
    list_filter = ['is_publish', 'is_available', 'is_deleted']


@admin.register(Relationship)
class RelationshipmAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'info']
    list_filter = ['is_publish', 'is_available', 'is_deleted']