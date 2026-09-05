import json
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


    def test_summary_create_serializer_empty_transcript(self):
        empty_transcript = Transcript.objects.create(
            user=self.user,
            title='Empty Transcript',
            file_name='empty.mp3',
            file_size=1024,
            file_type='audio/mpeg',
            status='completed',
            raw_text=''
        )
        serializer = SummaryCreateSerializer(
            data={'transcript_id': empty_transcript.id},
            context={'request': MagicMock(user=self.user)}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('no text to summarize', str(serializer.errors))

    def test_summary_create_serializer_other_user_transcript(self):
        other_user = User.objects.create_user(
            username='otheruser', email='other@example.com', password='password123'
        )
        other_transcript = Transcript.objects.create(
            user=other_user,
            title='Other Transcript',
            file_name='other.mp3',
            file_size=1024,
            file_type='audio/mpeg',
            status='completed',
            raw_text='Valid raw text'
        )
        serializer = SummaryCreateSerializer(
            data={'transcript_id': other_transcript.id},
            context={'request': MagicMock(user=self.user)}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("doesn't belong to you", str(serializer.errors))

    def test_summary_create_serializer_duplicate_summary(self):
        Summary.objects.create(
            transcript=self.transcript,
            user=self.user,
            status='completed',
            main_summary='Existing summary'
        )
        serializer = SummaryCreateSerializer(
            data={'transcript_id': self.transcript.id},
            context={'request': MagicMock(user=self.user)}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('Summary already exists', str(serializer.errors))
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


class SummaryTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='taskuser', email='taskuser@example.com', password='password123'
        )
        self.transcript = Transcript.objects.create(
            user=self.user,
            title='Lecture on Machine Learning',
            file_name='lecture.mp3',
            file_size=2048,
            file_type='audio/mpeg',
            status='completed',
            raw_text='Today we covered supervised learning, neural networks, and gradient descent algorithms.'
        )
        self.summary = Summary.objects.create(
            transcript=self.transcript,
            user=self.user,
            status='pending'
        )

    @patch('apps.summarizer.tasks.OpenAI')
    def test_generate_summary_task_success(self, mock_openai_cls):
        """Test successful summary generation with mocked DeepSeek OpenAI SDK call"""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.output_text = json.dumps({
            "main_summary": "This is a detailed overview of the machine learning lecture covering core models.",
            "key_points": ["Supervised learning requires labeled data", "Neural networks use gradient descent"],
            "questions": ["How does gradient descent adjust weights?"],
            "highlights": ["Gradient descent is foundational to deep learning"],
            "topics": ["Machine Learning", "Neural Networks"],
            "action_items": ["Review gradient descent math"]
        })
        mock_client.responses.create.return_value = mock_response

        with self.settings(DEEPSEEK_API_KEY='test-key', SUMMARY_MODEL='deepseek-v4-flash'):
            from .tasks import generate_summary_task
            result = generate_summary_task(self.summary.id)

        self.summary.refresh_from_db()
        self.assertEqual(self.summary.status, 'completed')
        self.assertEqual(self.summary.model_used, 'deepseek-v4-flash')
        self.assertTrue(self.summary.main_summary.startswith('This is a detailed overview'))
        self.assertEqual(len(self.summary.key_points), 2)
        self.assertEqual(len(self.summary.questions), 1)
        self.assertEqual(len(self.summary.highlights), 1)
        self.assertEqual(len(self.summary.topics), 2)
        self.assertEqual(len(self.summary.action_items), 1)
        self.assertGreater(self.summary.word_count, 0)
        self.assertIsNotNone(self.summary.processing_time)
        self.assertIsNotNone(self.summary.completed_at)
        self.assertEqual(self.summary.error_message, '')
        self.assertEqual(result['status'], 'completed')
        mock_client.responses.create.assert_called_once()
        call_kwargs = mock_client.responses.create.call_args.kwargs
        self.assertEqual(call_kwargs['model'], 'deepseek-v4-flash')
        self.assertEqual(call_kwargs['text']['format']['type'], 'json_schema')
        self.assertTrue(call_kwargs['text']['format']['strict'])
        self.assertEqual(call_kwargs['reasoning'], {'effort': 'none'})
        self.assertEqual(call_kwargs['extra_body'], {'thinking': {'type': 'disabled'}})

    @patch('apps.summarizer.tasks.OpenAI')
    def test_generate_summary_task_api_failure(self, mock_openai_cls):
        """Test task marks summary failed and records error message when API fails"""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.responses.create.side_effect = RuntimeError("DeepSeek service timeout")

        with self.settings(DEEPSEEK_API_KEY='test-key', SUMMARY_MODEL='deepseek-v4-flash'):
            from .tasks import generate_summary_task
            with self.assertRaises(RuntimeError):
                generate_summary_task(self.summary.id)

        self.summary.refresh_from_db()
        self.assertEqual(self.summary.status, 'failed')
        self.assertIn("DeepSeek service timeout", self.summary.error_message)

    def test_generate_summary_task_missing_api_key(self):
        """Test task fails gracefully when DEEPSEEK_API_KEY is not configured"""
        with self.settings(DEEPSEEK_API_KEY=None):
            from .tasks import generate_summary_task
            with self.assertRaises(ValueError):
                generate_summary_task(self.summary.id)

        self.summary.refresh_from_db()
        self.assertEqual(self.summary.status, 'failed')
        self.assertIn("DeepSeek API key not configured", self.summary.error_message)

    def test_generate_summary_task_missing_transcript_text(self):
        """Test task fails when transcript has no raw text"""
        self.transcript.raw_text = ''
        self.transcript.save()

        with self.settings(DEEPSEEK_API_KEY='test-key'):
            from .tasks import generate_summary_task
            with self.assertRaises(ValueError):
                generate_summary_task(self.summary.id)

        self.summary.refresh_from_db()
        self.assertEqual(self.summary.status, 'failed')

    def test_validate_summary_data_strict_validation(self):
        """Test _validate_summary_data strictly validates types and rejects non-strings"""
        from .tasks import _validate_summary_data

        base_valid = {
            "main_summary": "Valid summary",
            "key_points": ["Point 1"],
            "questions": ["Question 1?"],
            "highlights": ["Highlight 1"],
            "topics": ["Topic 1"],
            "action_items": ["Action 1"]
        }
        # Should succeed with valid data
        validated = _validate_summary_data(base_valid)
        self.assertEqual(validated["main_summary"], "Valid summary")
        self.assertEqual(validated["key_points"], ["Point 1"])

        # Rejects dict in array
        with self.assertRaises(ValueError) as ctx:
            bad_dict = {**base_valid, "topics": [{"name": "Machine Learning"}]}
            _validate_summary_data(bad_dict)
        self.assertIn("must be a string, got dict", str(ctx.exception))

        # Rejects integer in array
        with self.assertRaises(ValueError) as ctx:
            bad_int = {**base_valid, "questions": [101]}
            _validate_summary_data(bad_int)
        self.assertIn("must be a string, got int", str(ctx.exception))

        # Rejects boolean in array
        with self.assertRaises(ValueError) as ctx:
            bad_bool = {**base_valid, "highlights": [True]}
            _validate_summary_data(bad_bool)
        self.assertIn("must be a string, got bool", str(ctx.exception))

        # Rejects null in array
        with self.assertRaises(ValueError) as ctx:
            bad_none = {**base_valid, "key_points": [None]}
            _validate_summary_data(bad_none)
        self.assertIn("must be a string, got NoneType", str(ctx.exception))

        # Rejects empty string element in array
        with self.assertRaises(ValueError) as ctx:
            bad_empty = {**base_valid, "action_items": ["   "]}
            _validate_summary_data(bad_empty)
        self.assertIn("cannot be an empty string", str(ctx.exception))

        # Rejects non-string main_summary
        with self.assertRaises(ValueError) as ctx:
            bad_main = {**base_valid, "main_summary": 12345}
            _validate_summary_data(bad_main)
        self.assertIn("must be a non-empty string", str(ctx.exception))

        # Rejects missing required field
        with self.assertRaises(ValueError) as ctx:
            missing_field = {"main_summary": "Only summary"}
            _validate_summary_data(missing_field)
        self.assertIn("Missing required field", str(ctx.exception))

    @patch('apps.summarizer.tasks.OpenAI')
    def test_generate_summary_task_invalid_structure_fails(self, mock_openai_cls):
        """Test task marks summary failed and raises when model returns malformed structure"""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.output_text = json.dumps({
            "main_summary": "Valid overview",
            "key_points": ["Valid point"],
            "questions": ["Valid question?"],
            "highlights": ["Valid highlight"],
            "topics": [{"name": "Should not be a dict"}],
            "action_items": []
        })
        mock_client.responses.create.return_value = mock_response

        with self.settings(DEEPSEEK_API_KEY='test-key'):
            from .tasks import generate_summary_task
            with self.assertRaises(ValueError):
                generate_summary_task(self.summary.id)

        self.summary.refresh_from_db()
        self.assertEqual(self.summary.status, 'failed')
        self.assertIn("must be a string, got dict", self.summary.error_message)


class SummaryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser', email='apiuser@example.com', password='password123'
        )
        self.transcript = Transcript.objects.create(
            user=self.user,
            title='Completed Meeting',
            file_name='meeting.mp3',
            file_size=1024,
            file_type='audio/mpeg',
            status='completed',
            raw_text='Meeting discussion regarding Q3 goals and milestones.'
        )
        self.client.force_authenticate(user=self.user)

    @patch('apps.summarizer.tasks.generate_summary_task.delay')
    def test_create_summary_api_success(self, mock_task):
        """Test POST /api/summarizer/summaries/ creates summary and enqueues Celery task"""
        url = reverse('summary-list')
        response = self.client.post(url, {'transcript_id': self.transcript.id})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['transcript_id'], self.transcript.id)
        self.assertEqual(response.data['status'], 'pending')
        mock_task.assert_called_once()

    @patch('apps.summarizer.tasks.generate_summary_task.delay')
    def test_regenerate_summary_api_success(self, mock_task):
        """Test POST /api/summarizer/summaries/{id}/regenerate/ resets state and queues task"""
        summary = Summary.objects.create(
            transcript=self.transcript,
            user=self.user,
            status='completed',
            main_summary='Old summary content',
            key_points=['Old point']
        )
        url = reverse('summary-regenerate', kwargs={'pk': summary.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        summary.refresh_from_db()
        self.assertEqual(summary.status, 'pending')
        self.assertEqual(summary.main_summary, '')
        self.assertEqual(summary.key_points, [])
        mock_task.assert_called_once_with(summary.id)

    def test_regenerate_summary_when_processing_fails(self):
        """Test regeneration rejected when summary is currently processing"""
        summary = Summary.objects.create(
            transcript=self.transcript,
            user=self.user,
            status='processing'
        )
        url = reverse('summary-regenerate', kwargs={'pk': summary.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('currently being processed', response.data['error'])
