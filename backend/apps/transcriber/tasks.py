from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import Transcript
import whisper
import os
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def transcribe_audio_task(self, transcript_id):
    try:
        transcript = Transcript.objects.get(id=transcript_id)
        transcript.status = 'processing'
        transcript.save()
        
        logger.info(f"Starting transcription for transcript {transcript_id}")
        
        model_name = getattr(settings, 'WHISPER_MODEL', 'base')
        device = getattr(settings, 'WHISPER_DEVICE', 'cpu')
        
        model = whisper.load_model(model_name, device=device)
        
        file_path = transcript.file.path
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        result = model.transcribe(file_path)
        
        transcript.raw_text = result['text']
        transcript.language = result.get('language', '')
        
        if 'segments' in result and result['segments']:
            confidences = [seg.get('avg_logprob', 0) for seg in result['segments'] if 'avg_logprob' in seg]
            if confidences:
                transcript.confidence = sum(confidences) / len(confidences)
        
        if 'segments' in result and result['segments']:
            last_segment = result['segments'][-1]
            transcript.duration = last_segment.get('end', 0)
        
        transcript.status = 'completed'
        transcript.completed_at = timezone.now()
        transcript.save()
        
        logger.info(f"Transcription completed for transcript {transcript_id}")
        
        return {
            'transcript_id': transcript_id,
            'status': 'completed',
            'text_length': len(transcript.raw_text),
            'language': transcript.language,
            'duration': transcript.duration
        }
        
    except Transcript.DoesNotExist:
        logger.error(f"Transcript {transcript_id} not found")
        return {'error': f'Transcript {transcript_id} not found'}
        
    except Exception as e:
        logger.error(f"Transcription failed for transcript {transcript_id}: {str(e)}")
        
        try:
            transcript = Transcript.objects.get(id=transcript_id)
            transcript.status = 'failed'
            transcript.error_message = str(e)
            transcript.save()
        except Transcript.DoesNotExist:
            pass
        
        return {
            'transcript_id': transcript_id,
            'status': 'failed',
            'error': str(e)
        }
