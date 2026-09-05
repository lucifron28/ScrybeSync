import json
import logging
import time
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from openai import OpenAI
from .models import Summary

logger = logging.getLogger(__name__)

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "main_summary": {
            "type": "string",
            "description": "A concise 2-4 paragraph overview of the transcript."
        },
        "key_points": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Important concepts, facts, arguments, or decisions."
        },
        "questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Review, reflection, or discussion questions based on the transcript."
        },
        "highlights": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Important statements, excerpts, or notable concepts from the transcript."
        },
        "topics": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Main themes or topics covered, using short labels."
        },
        "action_items": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Actual tasks, decisions, recommendations, or next steps mentioned (empty array if none)."
        }
    },
    "required": [
        "main_summary",
        "key_points",
        "questions",
        "highlights",
        "topics",
        "action_items"
    ],
    "additionalProperties": False
}


def _validate_summary_data(data):
    """
    Validate that the LLM response conforms to the required summary schema.
    """
    if not isinstance(data, dict):
        raise ValueError("Summary response must be a JSON object")

    required_fields = [
        "main_summary",
        "key_points",
        "questions",
        "highlights",
        "topics",
        "action_items"
    ]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field in summary response: {field}")

    if not isinstance(data["main_summary"], str):
        raise ValueError("Field 'main_summary' must be a string")

    array_fields = ["key_points", "questions", "highlights", "topics", "action_items"]
    validated = {"main_summary": data["main_summary"].strip()}

    for field in array_fields:
        val = data[field]
        if not isinstance(val, list):
            raise ValueError(f"Field '{field}' must be a list of strings")
        validated[field] = [str(item).strip() for item in val if str(item).strip()]

    return validated


def _generate_deepseek_summary(transcript_text, client=None, model=None):
    """
    Generate structured summary using DeepSeek via the official OpenAI Python SDK.
    """
    model_name = model or getattr(settings, 'SUMMARY_MODEL', 'deepseek-v4-flash')

    if client is None:
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        if not api_key:
            raise ValueError("DeepSeek API key not configured")
        base_url = getattr(settings, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        client = OpenAI(api_key=api_key, base_url=base_url)

    system_prompt = (
        "You are an expert transcription summarizer. You summarize only the supplied transcript. "
        "Do not invent facts. Preserve uncertainty. Do not fabricate quotes. "
        "If no action items are mentioned, return an empty list for action_items. "
        "You must respond with valid JSON adhering strictly to this schema:\n"
        f"{json.dumps(SUMMARY_SCHEMA, indent=2)}"
    )

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Transcript to summarize:\n\n{transcript_text}"}
            ],
            response_format={"type": "json_object"},
            extra_body={"thinking": {"type": "disabled"}},
            temperature=0.3,
            max_tokens=2048,
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response received from DeepSeek API")

        parsed_json = json.loads(content)
        validated_data = _validate_summary_data(parsed_json)
        validated_data['model_used'] = model_name
        return validated_data

    except Exception as e:
        logger.error(f"DeepSeek API error: {str(e)}")
        raise e


@shared_task(bind=True)
def generate_summary_task(self, summary_id):
    """
    Celery task to generate AI summary from transcript text using DeepSeek V4 Flash.
    """
    try:
        summary = Summary.objects.get(id=summary_id)
        summary.status = 'processing'
        summary.save()

        logger.info(f"Starting summary generation for summary {summary_id}")

        api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        if not api_key:
            raise ValueError("DeepSeek API key not configured")

        transcript_text = summary.transcript.raw_text
        if not transcript_text:
            raise ValueError("No transcript text available")

        model_name = getattr(settings, 'SUMMARY_MODEL', 'deepseek-v4-flash')
        base_url = getattr(settings, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        client = OpenAI(api_key=api_key, base_url=base_url)

        start_time = time.time()
        result = _generate_deepseek_summary(transcript_text, client=client, model=model_name)
        processing_time = time.time() - start_time

        summary.main_summary = result['main_summary']
        summary.key_points = result['key_points']
        summary.questions = result['questions']
        summary.highlights = result['highlights']
        summary.topics = result['topics']
        summary.action_items = result['action_items']
        summary.word_count = len(summary.main_summary.split()) if summary.main_summary else 0
        summary.processing_time = processing_time
        summary.model_used = result.get('model_used', model_name)
        summary.status = 'completed'
        summary.completed_at = timezone.now()
        summary.error_message = ''
        summary.save()

        logger.info(f"Summary generation completed for summary {summary_id}")
        return {
            'summary_id': summary_id,
            'status': 'completed',
            'model_used': summary.model_used,
            'processing_time': processing_time,
            'word_count': summary.word_count
        }

    except Summary.DoesNotExist:
        logger.error(f"Summary {summary_id} not found")
        return {'error': f'Summary {summary_id} not found'}

    except Exception as e:
        logger.error(f"Summary generation failed for summary {summary_id}: {str(e)}")
        if 'summary' in locals():
            summary.status = 'failed'
            summary.error_message = str(e)
            summary.save()
        raise e
