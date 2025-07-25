from rest_framework import serializers
from django.conf import settings
from .models import Transcript
import os

class TranscriptUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    
    class Meta:
        model = Transcript
        fields = ['file', 'title']
    
    def validate_file(self, value):
        max_size = self._parse_size(getattr(settings, 'MAX_UPLOAD_SIZE', '100MB'))
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE}"
            )
        
        file_extension = os.path.splitext(value.name)[1].lower()
        allowed_extensions = []
        
        if hasattr(settings, 'ALLOWED_AUDIO_FORMATS'):
            allowed_extensions.extend([f'.{ext}' for ext in settings.ALLOWED_AUDIO_FORMATS])
        if hasattr(settings, 'ALLOWED_VIDEO_FORMATS'):
            allowed_extensions.extend([f'.{ext}' for ext in settings.ALLOWED_VIDEO_FORMATS])
        
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type {file_extension} is not supported. "
                f"Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        return value
    
    def _parse_size(self, size_str):
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def create(self, validated_data):
        file = validated_data['file']
        validated_data['file_name'] = file.name
        validated_data['file_size'] = file.size
        validated_data['file_type'] = file.content_type
        validated_data['user'] = self.context['request'].user
        
        if not validated_data.get('title'):
            validated_data['title'] = os.path.splitext(file.name)[0]
        
        return super().create(validated_data)

class TranscriptSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_extension = serializers.ReadOnlyField()
    is_audio = serializers.ReadOnlyField()
    is_video = serializers.ReadOnlyField()
    
    class Meta:
        model = Transcript
        fields = [
            'id', 'title', 'file_name', 'file_size', 'file_type', 'file_url',
            'file_extension', 'is_audio', 'is_video', 'status', 'raw_text',
            'duration', 'language', 'confidence', 'error_message',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'file_name', 'file_size', 'file_type', 'file_url',
            'file_extension', 'is_audio', 'is_video', 'status', 'raw_text',
            'duration', 'language', 'confidence', 'error_message',
            'created_at', 'updated_at', 'completed_at'
        ]
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None

class TranscriptListSerializer(serializers.ModelSerializer):
    file_extension = serializers.ReadOnlyField()
    is_audio = serializers.ReadOnlyField()
    is_video = serializers.ReadOnlyField()
    
    class Meta:
        model = Transcript
        fields = [
            'id', 'title', 'file_name', 'file_size', 'file_type',
            'file_extension', 'is_audio', 'is_video', 'status',
            'duration', 'language', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = fields
