from django.contrib import admin

from .models import Package, Release


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'programming_language', 'rank',
        'description', 'status',
    )
    search_fields = (
        'name', 'description', 'keywords',
        'repository',
    )
    readonly_fields = (
        'message', 'created', 'modified',
    )
    list_filter = (
        'programming_language', 'status',
        'rank', 'created',
    )


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = (
        'package', 'name', 'stable', 'status',
        'created',
    )
    search_fields = (
        'name', 'package__name',
    )
    readonly_fields = (
        'created', 'modified',
    )
    list_filter = (
        'package__programming_language',
        'status', 'package__rank', 'created',
    )
    autocomplete_fields = (
        'package',
    )
