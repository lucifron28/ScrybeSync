from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
from .models import Summary
from apps.transcriber.models import Transcript
from .serializers import SummaryCreateSerializer, SummarySerializer

User = get_user_model()

class SummaryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.transcript = Transcript.objects.create(
            user=self.user,
            title='Test Transcript',
            file_name='test.mp3',
            file_size=1024,
            file_type='audio/mpeg',
            status='completed',
            raw_text='This is a test transcript for summarization.'
        )

    def test_summary_creation(self):
        summary = Summary.objects.create(
            transcript=self.transcript,
            user=self.user,
            status='pending'
        )

        self.assertEqual(summary.transcript, self.transcript)
        self.assertEqual(summary.user, self.user)
        self.assertEqual(summary.status, 'pending')
        self.assertFalse(summary.has_content)

    def test_summary_with_content(self):
        summary = Summary.objects.create(
            transcript=self.transcript,
            user=self.user,
            status='completed',
            main_summary='This is a test summary.',
            key_points=['Point 1', 'Point 2'],
            questions=['Question 1?', 'Question 2?'],
            highlights=['Highlight 1', 'Highlight 2'],
            topics=['Topic 1', 'Topic 2'],
            action_items=['Action 1', 'Action 2'],
            word_count=5,
            model_used='gpt-3.5-turbo'
        )

        self.assertTrue(summary.has_content)
        self.assertEqual(summary.word_count, 5)
        self.assertEqual(len(summary.key_points), 2)
        self.assertEqual(len(summary.questions), 2)

    def test_has_content_property(self):
        summary = Summary.objects.create(
            transcript=self.transcript,
            user=self.user
        )

        self.assertFalse(summary.has_content)

        summary.main_summary = 'Test summary'
        self.assertTrue(summary.has_content)

        summary.main_summary = ''
        summary.key_points = ['Point 1']
        self.assertTrue(summary.has_content)

    def test_string_representation(self):
        summary = Summary(
            transcript=self.transcript,
            user=self.user
        )
        expected = f"Summary for {self.transcript.title} - {self.user.username}"
        self.assertEqual(str(summary), expected)


class SummarySerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.transcript = Transcript.objects.create(
            user=self.user,
            title='Test Transcript',
            file_name='test.mp3',
            file_size=1024,
            file_type='audio/mpeg',
            status='completed',
            raw_text='This is a test transcript for summarization.'
        )

    def test_summary_create_serializer_validation(self):
        data = {'transcript_id': self.transcript.id}
        request = MagicMock()
        request.user = self.user

        serializer = SummaryCreateSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())

    def test_summary_create_serializer_invalid_transcript(self):
        data = {'transcript_id': 99999}  # Non-existent transcript
        request = MagicMock()
        request.user = self.user

        serializer = SummaryCreateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('transcript_id', serializer.errors)

    def test_summary_create_serializer_incomplete_transcript(self):
        incomplete_transcript = Transcript.objects.create(
            user=self.user,
            title='Incomplete Transcript',
            file_name='incomplete.mp3',
            file_size=1024,
            file_type='audio/mpeg',
            status='pending' 
        )

        data = {'transcript_id': incomplete_transcript.id}
        request = MagicMock()
        request.user = self.user

        serializer = SummaryCreateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('must be completed', str(serializer.errors))

    def test_summary_serializer_fields(self):
        summary = Summary.objects.create(
            transcript=self.transcript,
            user=self.user,
            status='completed',
            main_summary='Test summary',
            key_points=['Point 1', 'Point 2'],
            word_count=2,
            model_used='gpt-3.5-turbo'
        )

        serializer = SummarySerializer(summary)
        data = serializer.data

        expected_fields = [
            'id', 'transcript_id', 'transcript_title', 'transcript_duration',
            'transcript_language', 'status', 'main_summary', 'key_points',
            'questions', 'highlights', 'topics', 'action_items', 'word_count',
            'processing_time', 'model_used', 'error_message', 'has_content',
            'created_at', 'updated_at', 'completed_at'
        ]

        for field in expected_fields:
            self.assertIn(field, data)
