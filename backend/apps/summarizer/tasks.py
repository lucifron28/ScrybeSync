from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import Summary
import google.generativeai as genai
import json
import time
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def generate_summary_task(self, summary_id):
    """
    Celery task to generate AI summary from transcript text using OpenAI API
    """
    try:
        summary = Summary.objects.get(id=summary_id)
        summary.status = 'processing'
        summary.save()
        
        logger.info(f"Starting summary generation for summary {summary_id}")

        # Check if Gemini API key is configured
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            raise ValueError("Gemini API key not configured")

        # Set up Gemini client
        genai.configure(api_key=api_key)
        
        # Get transcript text
        transcript_text = summary.transcript.raw_text
        if not transcript_text:
            raise ValueError("No transcript text available")
        
        start_time = time.time()

        # Generate summary using Gemini
        result = _generate_gemini_summary(transcript_text)

        processing_time = time.time() - start_time
        
        # Update summary with results
        summary.main_summary = result.get('main_summary', '')
        summary.key_points = result.get('key_points', [])
        summary.questions = result.get('questions', [])
        summary.highlights = result.get('highlights', [])
        summary.topics = result.get('topics', [])
        summary.action_items = result.get('action_items', [])
        summary.word_count = len(summary.main_summary.split()) if summary.main_summary else 0
        summary.processing_time = processing_time
        summary.model_used = result.get('model_used', 'gemini-1.5-flash')
        summary.status = 'completed'
        summary.completed_at = timezone.now()
        summary.save()
        
        logger.info(f"Summary generation completed for summary {summary_id}")
        
        return {
            'summary_id': summary_id,
            'status': 'completed',
            'word_count': summary.word_count,
            'processing_time': processing_time
        }
        
    except Summary.DoesNotExist:
        logger.error(f"Summary {summary_id} not found")
        return {'error': f'Summary {summary_id} not found'}
        
    except Exception as e:
        logger.error(f"Summary generation failed for summary {summary_id}: {str(e)}")
        
        try:
            summary = Summary.objects.get(id=summary_id)
            summary.status = 'failed'
            summary.error_message = str(e)
            summary.save()
        except Summary.DoesNotExist:
            pass
        
        return {
            'summary_id': summary_id,
            'status': 'failed',
            'error': str(e)
        }

def _generate_gemini_summary(transcript_text):
    """
    Generate summary using Google Gemini API
    """
    # Prepare the prompt
    prompt = f"""
Please analyze the following transcript and provide a comprehensive summary with the following components:

1. Main Summary: A concise overview of the content (2-3 paragraphs)
2. Key Points: 5-7 most important points discussed
3. Questions: 3-5 questions that arise from the content or could be used for further discussion
4. Highlights: 3-5 notable quotes or important statements
5. Topics: Main topics/themes covered
6. Action Items: Any tasks, decisions, or next steps mentioned

Please format your response as a JSON object with the following structure:
{{
    "main_summary": "...",
    "key_points": ["point 1", "point 2", ...],
    "questions": ["question 1", "question 2", ...],
    "highlights": ["highlight 1", "highlight 2", ...],
    "topics": ["topic 1", "topic 2", ...],
    "action_items": ["action 1", "action 2", ...]
}}

Transcript:
{transcript_text}
"""
    
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Generate content
        response = model.generate_content(prompt)

        content = response.text.strip()

        # Try to parse JSON response
        try:
            result = json.loads(content)
            result['model_used'] = 'gemini-1.5-flash'
            return result
        except json.JSONDecodeError:
            # If JSON parsing fails, create a basic summary
            return {
                'main_summary': content,
                'key_points': [],
                'questions': [],
                'highlights': [],
                'topics': [],
                'action_items': [],
                'model_used': 'gemini-1.5-flash'
            }

    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise e
