from django.contrib import admin

from .models import Package, Release, Log


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'technology', 'twitter_account', 'code_hosting', 'repository',)
    search_fields = ('name', 'technology', 'twitter_account', 'code_hosting', 'repository',)
    readonly_fields = ('created', 'modified',)


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'prerelease', 'published_at', 'status', 'package',)
    search_fields = ('name', 'body', 'prerelease', 'published_at', 'status', 'package',)
    readonly_fields = ('created', 'modified',)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id', 'content_object', 'message',)
    search_fields = ('content_type', 'object_id', 'content_object', 'message',)
    readonly_fields = ('created', 'modified',)