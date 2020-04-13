from django.contrib import admin

from .models import Package, Release


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'programming_language', 'source_type',
        'source_id', 'release_regex',
    )
    search_fields = (
        'name', 'source_id',
    )
    readonly_fields = (
        'description', 'site_url', 'tags',
        'created', 'modified',
    )
    list_filter = (
        'programming_language',
        'source_type',
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
        'package__programming_language',
        'status', 'created'
    )
    autocomplete_fields = (
        'package',
    )
