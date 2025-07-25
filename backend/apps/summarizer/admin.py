from django.contrib import admin
from .models import Summary

@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ['transcript', 'user', 'status', 'word_count', 'model_used', 'created_at']
    list_filter = ['status', 'model_used', 'created_at']
    search_fields = ['transcript__title', 'user__username', 'main_summary']
    readonly_fields = [
        'word_count', 'processing_time', 'model_used',
        'created_at', 'updated_at', 'completed_at'
    ]
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('transcript', 'user', 'status')
        }),
        ('Summary Content', {
            'fields': ('main_summary', 'key_points', 'questions', 'highlights', 'topics', 'action_items')
        }),
        ('Metadata', {
            'fields': ('word_count', 'processing_time', 'model_used', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
