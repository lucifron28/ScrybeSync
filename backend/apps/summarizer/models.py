from django.db import models
from django.contrib.auth import get_user_model
from apps.transcriber.models import Transcript

User = get_user_model()

class Summary(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    transcript = models.OneToOneField(
        Transcript,
        on_delete=models.CASCADE,
        related_name='summary'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='summaries'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Summary content fields
    main_summary = models.TextField(blank=True)
    key_points = models.JSONField(default=list, blank=True)
    questions = models.JSONField(default=list, blank=True)
    highlights = models.JSONField(default=list, blank=True)
    topics = models.JSONField(default=list, blank=True)
    action_items = models.JSONField(default=list, blank=True)

    # Metadata
    word_count = models.IntegerField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)  # Time in seconds
    model_used = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Summary for {self.transcript.title} - {self.user.username}"

    @property
    def has_content(self):
        """Check if summary has any content"""
        return bool(
            self.main_summary or
            self.key_points or
            self.questions or
            self.highlights or
            self.topics or
            self.action_items
        )

    class Meta:
        verbose_name_plural = "Summaries"
        ordering = ['-created_at']
