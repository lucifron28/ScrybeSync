from django.db import models
from django.contrib.auth import get_user_model
import os

User = get_user_model()

def upload_to_transcriber(instance, filename):
    """Generate upload path for transcriber files"""
    return f'transcriber/{instance.user.id}/{filename}'

class Transcript(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transcripts')
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=upload_to_transcriber)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    raw_text = models.TextField(blank=True)
    duration = models.FloatField(null=True, blank=True)  # Duration in seconds
    language = models.CharField(max_length=10, blank=True)  # Detected language
    confidence = models.FloatField(null=True, blank=True)  # Transcription confidence
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title or self.file_name} - {self.user.username}"

    @property
    def file_extension(self):
        return os.path.splitext(self.file_name)[1].lower()

    @property
    def is_audio(self):
        audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
        return self.file_extension in audio_extensions

    @property
    def is_video(self):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        return self.file_extension in video_extensions

    class Meta:
        ordering = ['-created_at']
