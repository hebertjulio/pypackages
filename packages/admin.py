from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'release', 'downloads', 'status',
    )
    search_fields = (
        'name',
    )
    readonly_fields = (
        'created', 'modified',
    )
    list_filter = (
        'status',
    )
