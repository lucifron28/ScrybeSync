from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Summary
from .serializers import SummaryCreateSerializer, SummarySerializer, SummaryListSerializer
from .tasks import generate_summary_task

class SummaryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Summary.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return SummaryCreateSerializer
        elif self.action == 'list':
            return SummaryListSerializer
        return SummarySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        summary = serializer.save()

        generate_summary_task.delay(summary.id)

        response_serializer = SummarySerializer(summary, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        summary = self.get_object()

        if summary.status == 'processing':
            return Response(
                {'error': 'Summary is currently being processed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        summary.status = 'pending'
        summary.error_message = ''
        summary.main_summary = ''
        summary.key_points = []
        summary.questions = []
        summary.highlights = []
        summary.topics = []
        summary.action_items = []
        summary.save()

        generate_summary_task.delay(summary.id)

        serializer = self.get_serializer(summary)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def status_summary(self, request):
        queryset = self.get_queryset()
        summary_data = {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'processing': queryset.filter(status='processing').count(),
            'completed': queryset.filter(status='completed').count(),
            'failed': queryset.filter(status='failed').count(),
        }
        return Response(summary_data)
