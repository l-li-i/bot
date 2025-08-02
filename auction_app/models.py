from django.db import models
from users_app.models import UserProfile # Импортируем нашу пользовательскую модель
from django.utils import timezone

class Lot(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает одобрения'),
        ('active', 'Активный'),
        ('scheduled', 'Запланирован'),
        ('completed', 'Завершен'),
        ('sold', 'Продан'),
        ('unsold', 'Не продан'),
        ('deleted', 'Удален'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название лота")
    description = models.TextField(verbose_name="Описание и доп. информация")
    start_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стартовая цена")
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Текущая цена")
    seller = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='selling_lots', verbose_name="Продавец")
    telegram_link = models.URLField(max_length=200, blank=True, null=True, verbose_name="Ссылка на продавца в Telegram")
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Геолокация товара")
    start_time = models.DateTimeField(verbose_name="Время старта")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус лота")
    document_type = models.CharField(max_length=20, choices=[
        ('jewelry', 'Ювелирный'),
        ('historical', 'Исторически ценный'),
        ('standard', 'Стандартный'),
    ], default='standard', verbose_name="Тип документа")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Лот"
        verbose_name_plural = "Лоты"
        ordering = ['-start_time']

    def __str__(self):
        return self.title

class LotImage(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='images', verbose_name="Лот")
    image = models.ImageField(upload_to='lot_images/', verbose_name="Изображение")

    class Meta:
        verbose_name = "Изображение лота"
        verbose_name_plural = "Изображения лотов"

    def __str__(self):
        return f"Image for {self.lot.title}"

class Bid(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='bids', verbose_name="Лот")
    bidder = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='bids_made', verbose_name="Участник")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма ставки")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время ставки")

    class Meta:
        verbose_name = "Ставка"
        verbose_name_plural = "Ставки"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Bid of {self.amount} by {self.bidder.username} on {self.lot.title}"

class Transaction(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Лот")
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="Пользователь")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    transaction_type = models.CharField(max_length=50, verbose_name="Тип транзакции") # 'deposit', 'withdrawal', 'lot_payment', 'commission'
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время транзакции")
    is_paid = models.BooleanField(default=False, verbose_name="Оплачено") # Для отслеживания оплаты лота

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} by {self.user.username}"
