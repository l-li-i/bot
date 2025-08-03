from django.db import models
from django.conf import settings
from django.utils import timezone
from users_app.models import UserProfile
from auction_app.models import Lot

# Модель для жалоб
class Complaint(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В ожидании'),
        ('resolved', 'Решено'),
        ('rejected', 'Отклонено'),
    )

    reporter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reported_complaints', verbose_name="Кто пожаловался")
    message = models.TextField(verbose_name="Текст жалобы")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    resolved_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_complaints', verbose_name="Решено модератором")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата решения")

    class Meta:
        verbose_name = "Жалоба"
        verbose_name_plural = "Жалобы"

    def __str__(self):
        return f"Жалоба от {self.reporter.username} - {self.status}"


# Модель для одобрения лотов
class LotApproval(models.Model):
    lot = models.OneToOneField(Lot, on_delete=models.CASCADE, related_name='approval', verbose_name="Лот")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен")
    approved_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_lots', verbose_name="Одобрен модератором")
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата одобрения")

    class Meta:
        verbose_name = "Одобрение лота"
        verbose_name_plural = "Одобрение лотов"

    def __str__(self):
        return f"Одобрение для лота '{self.lot.title}' - {'Да' if self.is_approved else 'Нет'}"
