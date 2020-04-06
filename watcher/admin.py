from django.contrib import admin

from .models import Package, Release


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
