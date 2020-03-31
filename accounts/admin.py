from django.utils.translation import gettext_lazy as _

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (_('Personal info'), {'fields': (
            'name', 'email', 'username', 'password',)}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'user_permissions',),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'created', 'modified',)}),
    )
    list_display = (
        'name', 'username', 'email', 'is_active',
        'is_staff', 'is_superuser',
    )
    search_fields = (
        'username', 'name', 'email',
    )
    readonly_fields = (
        'last_login', 'created', 'modified',
    )
    add_fieldsets = (
        (None, {
            'fields': ('name', 'email',),
        }),
    ) + BaseUserAdmin.add_fieldsets
