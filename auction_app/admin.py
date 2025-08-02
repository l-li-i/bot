from django.contrib import admin
from .models import Lot, LotImage, Bid, Transaction

class LotImageInline(admin.TabularInline):
    model = LotImage
    extra = 1 # количество пустых форм для добавления изображений

@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'start_price', 'current_price', 'status', 'start_time', 'end_time', 'document_type')
    list_filter = ('status', 'document_type', 'seller')
    search_fields = ('title', 'description', 'seller__username')
    inlines = [LotImageInline]
    actions = ['mark_as_active', 'mark_as_scheduled', 'mark_as_pending']

    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
    mark_as_active.short_description = "Отметить выбранные лоты как 'Активные'"

    def mark_as_scheduled(self, request, queryset):
        queryset.update(status='scheduled')
    mark_as_scheduled.short_description = "Отметить выбранные лоты как 'Запланированные'"

    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
    mark_as_pending.short_description = "Отметить выбранные лоты как 'Ожидающие одобрения'"


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('lot', 'bidder', 'amount', 'timestamp')
    list_filter = ('lot', 'bidder')
    search_fields = ('lot__title', 'bidder__username')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'timestamp', 'is_paid', 'lot')
    list_filter = ('transaction_type', 'is_paid', 'user')
    search_fields = ('user__username', 'lot__title')
