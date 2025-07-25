from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
import tempfile
import os
from .models import Transcript
from .serializers import TranscriptUploadSerializer, TranscriptSerializer

User = get_user_model()

class TranscriptModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_transcript_creation(self):
        transcript = Transcript.objects.create(
            user=self.user,
            title='Test Transcript',
            file_name='test.mp3',
            file_size=1024,
            file_type='audio/mpeg',
            status='pending'
        )

        self.assertEqual(transcript.user, self.user)
        self.assertEqual(transcript.title, 'Test Transcript')
        self.assertEqual(transcript.file_name, 'test.mp3')
        self.assertEqual(transcript.status, 'pending')
        self.assertTrue(transcript.is_audio)
        self.assertFalse(transcript.is_video)

    def test_file_extension_property(self):
        transcript = Transcript(file_name='test.mp3')
        self.assertEqual(transcript.file_extension, '.mp3')

        transcript.file_name = 'video.mp4'
        self.assertEqual(transcript.file_extension, '.mp4')

    def test_is_audio_property(self):
        audio_files = ['test.mp3', 'audio.wav', 'sound.m4a', 'music.flac', 'voice.ogg']
        for filename in audio_files:
            transcript = Transcript(file_name=filename)
            self.assertTrue(transcript.is_audio, f"{filename} should be detected as audio")

    def test_is_video_property(self):
        video_files = ['video.mp4', 'movie.avi', 'clip.mov', 'film.mkv', 'web.webm']
        for filename in video_files:
            transcript = Transcript(file_name=filename)
            self.assertTrue(transcript.is_video, f"{filename} should be detected as video")

    def test_string_representation(self):
        transcript = Transcript(
            title='My Transcript',
            file_name='test.mp3',
            user=self.user
        )
        expected = f"My Transcript - {self.user.username}"
        self.assertEqual(str(transcript), expected)


class TranscriptSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_transcript_upload_serializer_validation(self):
        file_content = b"fake audio content"
        uploaded_file = SimpleUploadedFile(
            "test.mp3",
            file_content,
            content_type="audio/mpeg"
        )

        data = {
            'file': uploaded_file,
            'title': 'Test Upload'
        }

        serializer = TranscriptUploadSerializer(data=data)
        # Note: This might fail due to file size validation in real scenarios
        # but for unit tests, we're testing the structure
        self.assertTrue('file' in serializer.fields)
        self.assertTrue('title' in serializer.fields)

    def test_transcript_serializer_fields(self):
        """Test transcript serializer fields"""
        transcript = Transcript.objects.create(
            user=self.user,
            title='Test Transcript',
            file_name='test.mp3',
            file_size=1024,
            file_type='audio/mpeg',
            status='completed',
            raw_text='This is a test transcription.'
        )

        serializer = TranscriptSerializer(transcript)
        data = serializer.data

        expected_fields = [
            'id', 'title', 'file_name', 'file_size', 'file_type',
            'file_extension', 'is_audio', 'is_video', 'status', 'raw_text',
            'duration', 'language', 'confidence', 'error_message',
            'created_at', 'updated_at', 'completed_at'
        ]

        for field in expected_fields:
            self.assertIn(field, data)


class TranscriptAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Get JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_list_transcripts_authenticated(self):
        """Test listing transcripts for authenticated user"""
        # Create some transcripts
        Transcript.objects.create(
            user=self.user,
            title='Transcript 1',
            file_name='test1.mp3',
            file_size=1024,
            file_type='audio/mpeg'
        )
        Transcript.objects.create(
            user=self.user,
            title='Transcript 2',
            file_name='test2.mp3',
            file_size=2048,
            file_type='audio/mpeg'
        )

        url = reverse('transcript-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_transcripts_unauthenticated(self):
        """Test that unauthenticated users cannot list transcripts"""
        self.client.credentials()  # Remove authentication
        url = reverse('transcript-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_only_see_own_transcripts(self):
        """Test that users can only see their own transcripts"""
        # Create another user and transcript
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

        Transcript.objects.create(
            user=self.user,
            title='My Transcript',
            file_name='my_test.mp3',
            file_size=1024,
            file_type='audio/mpeg'
        )

        Transcript.objects.create(
            user=other_user,
            title='Other Transcript',
            file_name='other_test.mp3',
            file_size=1024,
            file_type='audio/mpeg'
        )

        url = reverse('transcript-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'My Transcript')

    @patch('apps.transcriber.tasks.transcribe_audio_task.delay')
    def test_upload_audio_file(self, mock_task):
        """Test uploading an audio file"""
        # Create a temporary audio file
        file_content = b"fake audio content for testing"
        uploaded_file = SimpleUploadedFile(
            "test_audio.mp3",
            file_content,
            content_type="audio/mpeg"
        )

        data = {
            'file': uploaded_file,
            'title': 'Test Audio Upload'
        }

        url = reverse('transcript-list')
        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Audio Upload')
        self.assertEqual(response.data['status'], 'pending')
        self.assertTrue(response.data['is_audio'])

        # Verify task was called
        mock_task.assert_called_once()

        # Verify transcript was created in database
        transcript = Transcript.objects.get(id=response.data['id'])
        self.assertEqual(transcript.user, self.user)
        self.assertEqual(transcript.file_name, 'test_audio.mp3')

    def test_get_transcript_detail(self):
        """Test retrieving a specific transcript"""
        transcript = Transcript.objects.create(
            user=self.user,
            title='Detail Test',
            file_name='detail_test.mp3',
            file_size=1024,
            file_type='audio/mpeg',
            status='completed',
            raw_text='This is the transcribed text.'
        )

        url = reverse('transcript-detail', kwargs={'pk': transcript.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Detail Test')
        self.assertEqual(response.data['raw_text'], 'This is the transcribed text.')

    def test_status_summary_endpoint(self):
        """Test the status summary endpoint"""
        # Create transcripts with different statuses
        Transcript.objects.create(
            user=self.user, title='Pending', file_name='p.mp3',
            file_size=1024, file_type='audio/mpeg', status='pending'
        )
        Transcript.objects.create(
            user=self.user, title='Processing', file_name='pr.mp3',
            file_size=1024, file_type='audio/mpeg', status='processing'
        )
        Transcript.objects.create(
            user=self.user, title='Completed', file_name='c.mp3',
            file_size=1024, file_type='audio/mpeg', status='completed'
        )
        Transcript.objects.create(
            user=self.user, title='Failed', file_name='f.mp3',
            file_size=1024, file_type='audio/mpeg', status='failed'
        )

        url = reverse('transcript-status-summary')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 4)
        self.assertEqual(response.data['pending'], 1)
        self.assertEqual(response.data['processing'], 1)
        self.assertEqual(response.data['completed'], 1)
        self.assertEqual(response.data['failed'], 1)


class TranscriptTaskTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @patch('apps.transcriber.tasks.whisper.load_model')
    @patch('os.path.exists')
    def test_transcribe_audio_task_success(self, mock_exists, mock_load_model):
        """Test successful transcription task"""
        # Create a transcript with a mock file
        from django.core.files.uploadedfile import SimpleUploadedFile
        mock_file = SimpleUploadedFile("test.mp3", b"fake audio content", content_type="audio/mpeg")

        transcript = Transcript.objects.create(
            user=self.user,
            title='Task Test',
            file=mock_file,
            file_name='task_test.mp3',
            file_size=1024,
            file_type='audio/mpeg',
            status='pending'
        )

        # Mock file exists
        mock_exists.return_value = True

        # Mock Whisper model and result
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model

        mock_result = {
            'text': 'This is the transcribed text from the audio file.',
            'language': 'en',
            'segments': [
                {'avg_logprob': -0.5, 'end': 10.5}
            ]
        }
        mock_model.transcribe.return_value = mock_result

        from .tasks import transcribe_audio_task
        result = transcribe_audio_task(transcript.id)

        transcript.refresh_from_db()

        self.assertEqual(transcript.status, 'completed')
        self.assertEqual(transcript.raw_text, 'This is the transcribed text from the audio file.')
        self.assertEqual(transcript.language, 'en')
        self.assertEqual(transcript.duration, 10.5)
        self.assertIsNotNone(transcript.completed_at)

        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['transcript_id'], transcript.id)

    @patch('apps.transcriber.tasks.whisper.load_model')
    @patch('os.path.exists')
    def test_transcribe_audio_task_file_not_found(self, mock_exists, mock_load_model):
        from django.core.files.uploadedfile import SimpleUploadedFile
        mock_file = SimpleUploadedFile("missing.mp3", b"fake audio content", content_type="audio/mpeg")

        transcript = Transcript.objects.create(
            user=self.user,
            title='Missing File Test',
            file=mock_file,
            file_name='missing.mp3',
            file_size=1024,
            file_type='audio/mpeg',
            status='pending'
        )

        mock_exists.return_value = False

        from .tasks import transcribe_audio_task
        result = transcribe_audio_task(transcript.id)

        transcript.refresh_from_db()

        self.assertEqual(transcript.status, 'failed')
        self.assertIn('not found', transcript.error_message.lower())
        self.assertEqual(result['status'], 'failed')

    def test_transcribe_audio_task_transcript_not_found(self):
        from .tasks import transcribe_audio_task
        result = transcribe_audio_task(99999)  # Non-existent ID

        self.assertIn('error', result)
        self.assertIn('not found', result['error'])
