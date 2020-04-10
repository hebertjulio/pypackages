from django.contrib import admin

from .models import Package, Release


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'programming_language', 'repository_owner', 'repository_name',
        'release_regex', 'description',
    )
    search_fields = (
        'name', 'repository',
    )
    readonly_fields = (
        'description', 'home_page_url', 'hashtags',
        'created', 'modified',
    )
    list_filter = (
        'programming_language',
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
