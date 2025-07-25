from django.contrib import admin
from .models import Transcript

@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'file_name', 'file_size', 'duration', 'created_at']
    list_filter = ['status', 'language', 'created_at']
    search_fields = ['title', 'file_name', 'user__username']
    readonly_fields = ['file_size', 'file_type', 'raw_text', 'duration', 'language', 'confidence', 'created_at', 'updated_at', 'completed_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'status')
        }),
        ('File Information', {
            'fields': ('file', 'file_name', 'file_size', 'file_type')
        }),
        ('Transcription Results', {
            'fields': ('raw_text', 'duration', 'language', 'confidence', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
