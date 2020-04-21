from django.contrib import admin

from .models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'rank', 'description',
        'last_release', 'has_new_release', 'status',
    )
    search_fields = (
        'name', 'description', 'keywords',
        'repository',
    )
    readonly_fields = (
        'message', 'created', 'modified',
    )
    list_filter = (
        'has_new_release', 'status',
        'rank', 'created',
    )
