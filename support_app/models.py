from django.db import models
from users_app.models import UserProfile
from auction_app.models import Lot

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('resolved', 'Решена'),
        ('rejected', 'Отклонена'),
    ]

    reporter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reported_complaints', verbose_name="Подавший жалобу")
    target_admin = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_complaints', verbose_name="Администратор, на которого жалуются")
    message = models.TextField(verbose_name="Сообщение жалобы")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_complaints', verbose_name="Решена")

    class Meta:
        verbose_name = "Жалоба"
        verbose_name_plural = "Жалобы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Жалоба от {self.reporter.username} на {self.target_admin.username}"

class LotApproval(models.Model):
    lot = models.OneToOneField(Lot, on_delete=models.CASCADE, related_name='approval_status', verbose_name="Лот")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен")
    approved_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Одобрено")
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Причина отклонения")

    class Meta:
        verbose_name = "Одобрение лота"
        verbose_name_plural = "Одобрения лотов"

    def __str__(self):
        return f"Одобрение для лота {self.lot.title}: {'Да' if self.is_approved else 'Нет'}"
