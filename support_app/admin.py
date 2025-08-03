from django.contrib import admin
from .models import Complaint, LotApproval
from django.utils import timezone

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'resolved_by', 'status', 'created_at', 'resolved_by')
    list_filter = ('status', 'created_at')
    search_fields = ('reporterusername', 'target_adminusername', 'message')
    actions = ['mark_as_resolved', 'mark_as_rejected']

    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved', resolved_by=request.user, resolved_at=timezone.now())
    mark_as_resolved.short_description = "Отметить выбранные жалобы как 'Решены'"

    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected', resolved_by=request.user, resolved_at=timezone.now())
    mark_as_rejected.short_description = "Отметить выбранные жалобы как 'Отклонены'"

@admin.register(LotApproval)
class LotApprovalAdmin(admin.ModelAdmin):
    list_display = ('lot', 'is_approved', 'approved_by', 'approval_date')
    list_filter = ('is_approved',)
    search_fields = ('lot__title',)