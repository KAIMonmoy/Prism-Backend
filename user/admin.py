from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import PrismUser


class UserAdminConfig(UserAdmin):
    model = PrismUser
    search_fields = ('email', 'user_name')
    list_filter = ('email', 'user_name', 'is_staff')
    list_display = ('id', 'email', 'user_name', 'is_staff')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'user_name', 'first_name', 'last_name', 'address', 'phone')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )


admin.site.register(PrismUser, UserAdminConfig)
