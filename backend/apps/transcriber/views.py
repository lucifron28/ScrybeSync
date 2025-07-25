from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Transcript
from .serializers import TranscriptUploadSerializer, TranscriptSerializer, TranscriptListSerializer
from .tasks import transcribe_audio_task

class TranscriptViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Transcript.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return TranscriptUploadSerializer
        elif self.action == 'list':
            return TranscriptListSerializer
        return TranscriptSerializer

    def create(self, request, *args, **kwargs):
        """Upload and start transcription of audio/video file"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transcript = serializer.save()

        # Start transcription task
        transcribe_audio_task.delay(transcript.id)

        # Return the created transcript with full details
        response_serializer = TranscriptSerializer(transcript, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def retry_transcription(self, request, pk=None):
        """Retry transcription for a failed transcript"""
        transcript = self.get_object()

        if transcript.status not in ['failed', 'completed']:
            return Response(
                {'error': 'Can only retry failed transcriptions'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reset status and start transcription task
        transcript.status = 'pending'
        transcript.error_message = ''
        transcript.save()

        transcribe_audio_task.delay(transcript.id)

        serializer = self.get_serializer(transcript)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def status_summary(self, request):
        """Get summary of transcription statuses"""
        queryset = self.get_queryset()
        summary = {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'processing': queryset.filter(status='processing').count(),
            'completed': queryset.filter(status='completed').count(),
            'failed': queryset.filter(status='failed').count(),
        }
        return Response(summary)
