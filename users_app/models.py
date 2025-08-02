from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    successful_payments = models.IntegerField(default=0)
    strikes = models.IntegerField(default=0)
    is_admin = models.BooleanField(default=False)
    is_support = models.BooleanField(default=False)
    is_super_admin = models.BooleanField(default=False)
    can_autobid = models.BooleanField(default=False) # Доступ к автоставкам
    # Можно добавить поля для связи с телегой (username, first_name и т.д.) по необходим,

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return self.username or f"User {self.telegram_id}"
