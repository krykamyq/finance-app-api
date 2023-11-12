from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'username']
    fieldsets = (
        (None, {
            "fields": (
                'email', 'username', 'balance'
            ),
        }),
        (_('Permissions'), {
            "fields": (
                'is_staff',
                'is_active',
                'is_superuser'
            ),
        }),
        (_('Important dates'), {
            "fields": ('last_login', 'created_at')

        }),
    )
    readonly_fields = ['last_login', 'created_at']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Account)
admin.site.register(models.ActiveAccount)
admin.site.register(models.Transaction)
