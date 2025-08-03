from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile


class UserProfileAdmin(UserAdmin):
    # Поля, которые будут отображаться в списке пользователей
    list_display = ('username', 'telegram_id', 'is_admin', 'is_support', 'is_suspended', 'balance')

    # Поля, по которым можно будет фильтровать
    list_filter = ('is_admin', 'is_support', 'is_suspended')

    # Поля, по которым можно будет искать
    search_fields = ('username', 'telegram_id')

    # Поля, которые будут доступны только для чтения
    readonly_fields = ('date_joined', 'last_login')

    # Поля для сортировки по умолчанию
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права и разрешения', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin', 'is_support', 'is_suspended', 'groups',
                       'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
        ('Информация Telegram', {'fields': ('telegram_id', 'phone_number')}),
        ('Финансовая информация', {'fields': ('balance', 'success_payments_count')}),
    )

    # Добавление полей в формы для создания и редактирования пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'telegram_id', 'email', 'phone_number', 'is_admin', 'is_support', 'is_suspended',
                       'balance', 'success_payments_count')
        }),
    )


admin.site.register(UserProfile, UserProfileAdmin)

