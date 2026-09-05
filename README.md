# ScrybeSync

ScrybeSync is a personal transcription and note-taking web application. It converts audio/video recordings into transcripts, generates summaries, and lets users organize the results as notes.

## Product Focus

ScrybeSync is a practical personal productivity tool, not a commercial SaaS application. It is designed for straightforward personal workflows:

* Uploading audio and video recordings
* Transcribing speech using OpenAI Whisper
* Generating summaries from completed transcripts
* Creating and organizing personal markdown notes

---

## Features

### Implemented
- **User Authentication**: Simple user registration, login, logout, HttpOnly refresh cookie rotation, and an authenticated `/api/users/me/` endpoint to restore user state.
- **Media Upload**: File upload support for common audio formats (`.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`) and video formats (`.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`).
- **Asynchronous Transcription**: Background transcription worker via Celery and OpenAI Whisper.
- **Retry Mechanism**: Dedicated retry endpoint strictly for failed transcriptions.
- **Transcript Summarization**: Asynchronous summary generation for completed transcripts using LLMs (Gemini).
- **Notes Management**: Create, view, update, and delete personal notes.
- **User-Isolated Categories**: Categories are scoped per user (e.g. two users can both create a "School" category, but a single user cannot create duplicates). Server-side validation prevents cross-user category assignment.
- **Practical Workspace**: Minimal dashboard featuring recent transcriptions, recent notes, and real item counts.
- **Theme Support**: Light and dark mode with persistent user preference.

### Planned
- **URL Import**: Direct media importing from YouTube and other video/audio platforms using `yt-dlp`.
- **Interactive Transcript Viewer**: Timed segment viewer with inline note-taking and section clipping.
- **Bi-directional Note Linking**: Interconnected personal wiki-style note references.

---

## Tech Stack

### Backend
- **Framework**: Django 5.2 & Django REST Framework
- **Database**: PostgreSQL (with SQLite support for local development/testing)
- **Task Queue**: Celery & Redis
- **Transcription Engine**: OpenAI Whisper & FFmpeg
- **LLM Integration**: Google Generative AI (Gemini)

### Frontend
- **Framework**: React 19 & Vite 6
- **Routing**: React Router 7
- **Styling**: Tailwind CSS 4
- **State Management**: Zustand
- **HTTP Client**: Axios

---

## API Endpoints

### Authentication & Users
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/users/register/` | Register a new user |
| `POST` | `/api/users/login/` | Authenticate with credentials; returns access token and sets HttpOnly refresh cookie |
| `POST` | `/api/users/token/refresh/` | Refresh access token using HttpOnly cookie |
| `POST` | `/api/users/logout/` | Invalidate refresh token and clear session |
| `GET` | `/api/users/me/` | Retrieve currently authenticated user profile |

### Transcripts
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/transcriber/transcripts/` | List current user's transcripts |
| `POST` | `/api/transcriber/transcripts/` | Upload audio/video file and queue transcription |
| `GET` | `/api/transcriber/transcripts/{id}/` | Retrieve transcript details and text |
| `POST` | `/api/transcriber/transcripts/{id}/retry_transcription/` | Retry a failed transcription |
| `GET` | `/api/transcriber/transcripts/status_summary/` | Get transcript count summary by status |
| `DELETE` | `/api/transcriber/transcripts/{id}/` | Delete a transcript |

### Summaries
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/summarizer/summaries/` | List current user's summaries |
| `POST` | `/api/summarizer/summaries/` | Generate summary for a completed transcript |
| `GET` | `/api/summarizer/summaries/{id}/` | Retrieve summary details |
| `POST` | `/api/summarizer/summaries/{id}/regenerate/` | Regenerate summary content |
| `GET` | `/api/summarizer/summaries/status_summary/` | Get summary count summary by status |
| `DELETE` | `/api/summarizer/summaries/{id}/` | Delete a summary |

### Notes & Categories
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/notes/notes/` | List current user's notes |
| `POST` | `/api/notes/notes/` | Create a note (server validates category ownership) |
| `GET` | `/api/notes/notes/{id}/` | Retrieve note details |
| `PATCH` | `/api/notes/notes/{id}/` | Update note content or category |
| `DELETE` | `/api/notes/notes/{id}/` | Delete a note |
| `GET` | `/api/notes/categories/` | List current user's categories |
| `POST` | `/api/notes/categories/` | Create a category (scoped uniquely per user) |
| `DELETE` | `/api/notes/categories/{id}/` | Delete a category |

---

## Configuration & Environment Variables

### Backend (`backend/.env`)
```bash
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (defaults to PostgreSQL, or set USE_SQLITE=True for local dev/testing)
USE_SQLITE=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=scrybesync_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AI & Media
GEMINI_API_KEY=your_gemini_api_key
WHISPER_MODEL=base
WHISPER_DEVICE=cpu
MAX_UPLOAD_SIZE=100MB
```

### Frontend (`frontend/.env`)
```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## Running Locally

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

To run Celery worker:
```bash
# Linux / macOS
celery -A backend worker -l info

# Windows (requires solo pool due to lack of fork support)
celery -A backend worker -l info --pool=solo
```
To run backend tests:
```bash
python manage.py test
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

To run frontend lint and build:
```bash
npm run lint
npm run build
```

---

## License

MIT
