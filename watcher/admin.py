from django.contrib import admin

from .models import Package, Release, Log


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'programming_language', 'code_hosting', 'repository_owner',
        'repository_name',
    )
    search_fields = (
        'name', 'repository',
    )
    readonly_fields = (
        'created', 'modified',
    )
    list_filter = (
        'programming_language', 'code_hosting',
    )


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = (
        'package', 'name', 'status',
    )
    search_fields = (
        'name', 'package',
    )
    readonly_fields = (
        'created', 'modified',
    )
    list_filter = (
        'created', 'status',
    )
    autocomplete_fields = (
        'package',
    )


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        'content_type', 'object_id', 'message', 'created',
    )
    search_fields = (
        'content_type', 'object_id', 'message',
    )
    readonly_fields = (
        'content_type', 'object_id', 'message',
        'created', 'modified',
    )
    list_filter = (
        'created',
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
