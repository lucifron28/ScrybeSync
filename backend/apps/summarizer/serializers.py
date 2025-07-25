from rest_framework import serializers
from .models import Summary
from apps.transcriber.models import Transcript

class SummaryCreateSerializer(serializers.ModelSerializer):
    transcript_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Summary
        fields = ['transcript_id']
    
    def validate_transcript_id(self, value):
        user = self.context['request'].user
        
        try:
            transcript = Transcript.objects.get(id=value, user=user)
        except Transcript.DoesNotExist:
            raise serializers.ValidationError("Transcript not found or doesn't belong to you")
        
        if transcript.status != 'completed':
            raise serializers.ValidationError("Transcript must be completed before summarization")
        
        if not transcript.raw_text:
            raise serializers.ValidationError("Transcript has no text to summarize")
        
        if hasattr(transcript, 'summary'):
            raise serializers.ValidationError("Summary already exists for this transcript")
        
        return value
    
    def create(self, validated_data):
        transcript_id = validated_data['transcript_id']
        transcript = Transcript.objects.get(id=transcript_id)
        
        summary = Summary.objects.create(
            transcript=transcript,
            user=self.context['request'].user,
            status='pending'
        )
        
        return summary

class SummarySerializer(serializers.ModelSerializer):
    transcript_title = serializers.CharField(source='transcript.title', read_only=True)
    transcript_id = serializers.IntegerField(source='transcript.id', read_only=True)
    transcript_duration = serializers.FloatField(source='transcript.duration', read_only=True)
    transcript_language = serializers.CharField(source='transcript.language', read_only=True)
    has_content = serializers.ReadOnlyField()
    
    class Meta:
        model = Summary
        fields = [
            'id', 'transcript_id', 'transcript_title', 'transcript_duration', 
            'transcript_language', 'status', 'main_summary', 'key_points', 
            'questions', 'highlights', 'topics', 'action_items', 'word_count', 
            'processing_time', 'model_used', 'error_message', 'has_content',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'transcript_id', 'transcript_title', 'transcript_duration',
            'transcript_language', 'status', 'main_summary', 'key_points',
            'questions', 'highlights', 'topics', 'action_items', 'word_count',
            'processing_time', 'model_used', 'error_message', 'has_content',
            'created_at', 'updated_at', 'completed_at'
        ]

class SummaryListSerializer(serializers.ModelSerializer):
    transcript_title = serializers.CharField(source='transcript.title', read_only=True)
    transcript_id = serializers.IntegerField(source='transcript.id', read_only=True)
    has_content = serializers.ReadOnlyField()
    
    class Meta:
        model = Summary
        fields = [
            'id', 'transcript_id', 'transcript_title', 'status', 
            'word_count', 'model_used', 'has_content',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = fields
