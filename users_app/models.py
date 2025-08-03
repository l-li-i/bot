from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Кастомная модель пользователя
class UserProfile(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Номер телефона")
    is_admin = models.BooleanField(default=False, verbose_name="Администратор")
    is_support = models.BooleanField(default=False, verbose_name="Сотрудник поддержки")
    is_super_admin = models.BooleanField(default=False, verbose_name="Супер-администратор")
    is_suspended = models.BooleanField(default=False, verbose_name="Заблокирован")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Баланс")
    last_activity = models.DateTimeField(default=timezone.now, verbose_name="Последняя активность")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Дата регистрации")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    success_payments_count = models.IntegerField(default=0, verbose_name="Количество успешных платежей")
    can_autobid = models.BooleanField(default=False, verbose_name="Разрешено автобид")
    strikes = models.IntegerField(default=0, verbose_name="Количество страйков")
    email = models.EmailField(blank=True, null=True, verbose_name="Email адрес")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"@{self.username} ({self.telegram_id})"