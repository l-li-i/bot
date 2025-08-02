from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

@admin.register(UserProfile)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('telegram_id', 'balance', 'successful_payments', 'strikes', 'is_admin', 'is_support', 'is_super_admin', 'can_autobid')}),
    )
    list_display = ('username', 'telegram_id', 'balance', 'is_admin', 'is_support', 'is_super_admin', 'strikes', 'is_staff')
    search_fields = ('username', 'telegram_id')
    list_filter = ('is_admin', 'is_support', 'is_super_admin', 'can_autobid')