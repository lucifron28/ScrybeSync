# WhisperNote: Transcription & Note-Taking Web App

A full-stack web application for uploading audio/video, transcribing with Whisper, summarizing via an LLM, and managing markdown-based linked notes.

## Project Goals
- **Rapid Prototyping**: MVP with file upload, transcription, and transcript viewer within the first week  
- **User-Centric UX**: Intuitive dashboard for managing transcripts and notes  
- **Scalable Architecture**: Celery + Redis for background tasks to handle multiple uploads concurrently  
- **Modular Codebase**: Separate concerns into `transcriber`, `summarizer`, `notes`, and `users` apps  
- **Secure by Default**: JWT-based auth, HTTPS-ready, environment-driven secrets  

## Table of Contents
1. [Features](#features)  
2. [Tech Stack](#tech-stack)  
3. [Project Structure](#project-structure)  
4. [System Design](#system-design)  
5. [Authentication](#authentication)  
6. [API Endpoints](#api-endpoints)  
7. [Getting Started](#getting-started)  
   - [Prerequisites](#prerequisites)  
   - [Installation](#installation)  
   - [Environment Variables](#environment-variables)  
   - [Running Locally](#running-locally)  
8. [Docker Setup](#docker-setup)  
9. [Frontend Setup](#frontend-setup)  
10. [Contributing](#contributing)  
11. [License](#license)  

---

## Features
- **File Upload**: Video/audio uploads with progress display  
- **Transcription**: High-quality speech-to-text via OpenAI Whisper  
- **Summarization**: LLM-powered extraction of questions, key points & highlights  
- **Raw Transcript Viewer**: Scrollable text output  
- **Notes**:  
  - Markdown editor & preview  
  - CRUD operations (Create, Read, Update, Delete)  
  - Bi-directional linked notes  
  - External link attachments  

## Tech Stack
- **Backend**: Python, Django 4.x, Django REST Framework, Celery  
- **Transcription**: Whisper (OpenAI) + FFmpeg  
- **LLM**: OpenAI API (GPT-4 / GPT-3.5) or local model  
- **Database**: PostgreSQL  
- **Async Broker**: Redis  
- **Frontend**: React 18.x, Vite, Tailwind CSS, React Router  
- **Markdown**: react-markdown, remark-gfm or @uiw/react-md-editor  
- **Containerization**: Docker & Docker Compose  

## Project Structure

```text
scrybesync/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── users/            # User registration, JWT auth
│   │   ├── transcriber/      # Upload, Whisper integration
│   │   ├── summarizer/       # LLM calls & parsing
│   │   └── notes/            # Note model, linking logic
│   ├── media/                # Uploaded files
│   └── logs/
│
└── frontend/
    ├── public/
    │   └── favicon.ico
    ├── src/
    │   ├── components/
    │   │   ├── Auth/         # Login, Register forms
    │   │   ├── Transcription/
    │   │   ├── Notes/
    │   │   └── Layout/
    │   ├── pages/
    │   │   ├── Dashboard.jsx
    │   │   ├── Transcribe.jsx
    │   │   ├── NotesList.jsx
    │   │   └── NoteDetail.jsx
    │   ├── hooks/
    │   ├── services/          # Axios API clients
    │   ├── App.jsx
    │   └── main.jsx
    ├── tailwind.config.js
    └── package.json
```

## System Design

1. **Client → API Gateway**  
   React frontend uses Axios to call DRF endpoints (with JWT in `Authorization` header).  

2. **API Server (Django + DRF)**  
   - **Upload Endpoint**: Accepts audio/video, saves to `media/`, enqueues Celery task  
   - **Transcription Worker** (Celery):  
     1. Downloads file  
     2. Runs Whisper (\`whisper.transcribe()\`)  
     3. Saves raw text to DB  
     4. Notifies user via polling or WebSocket  
   - **Summarization Worker** (Celery):  
     1. Takes transcript  
     2. Calls OpenAI API with prompts  
     3. Stores highlights, questions, summary JSON  

3. **Database (PostgreSQL)**  
   - **User**: \`username\`, \`email\`, \`password_hash\`  
   - **Transcript**: \`user\`, \`file_path\`, \`raw_text\`, \`status\`, \`created_at\`  
   - **Summary**: \`transcript\`, \`highlights\`, \`questions\`, \`notes\`, \`created_at\`  
   - **Note**: \`user\`, \`title\`, \`content (md)\`, \`linked_notes (M2M)\`, \`external_links (JSON)\`

4. **Cache & Broker (Redis)**  
   - Celery broker & result backend  
   - Optional caching of API responses  

## Authentication

- **Register**: \`POST /api/auth/register/\`  
  - Request: \`{ "username", "email", "password" }\`  
  - Response: \`{ "access", "refresh" }\`

- **Login**: \`POST /api/auth/login/\`  
  - Request: \`{ "username", "password" }\`  
  - Response: \`{ "access", "refresh" }\`

- **Refresh Token**: \`POST /api/auth/token/refresh/\`  
  - Request: \`{ "refresh" }\`  
  - Response: \`{ "access" }\`

- **Protected Endpoints** require \`Authorization: Bearer <access_token>\`

## API Endpoints

| Path                       | Method | Description                              |
|----------------------------|--------|------------------------------------------|
| \`/api/auth/register/\`      | POST   | Create user & return JWT tokens          |
| \`/api/auth/login/\`         | POST   | Authenticate & return JWT tokens         |
| \`/api/transcripts/\`        | POST   | Upload file → enqueue Whisper task       |
| \`/api/transcripts/\`        | GET    | List user’s transcripts & statuses       |
| \`/api/transcripts/{id}/\`   | GET    | Retrieve raw transcript & summary JSON   |
| \`/api/summaries/\`          | POST   | Trigger LLM summarization on a transcript|
| \`/api/notes/\`              | GET    | List all notes                           |
| \`/api/notes/\`              | POST   | Create a new markdown note               |
| \`/api/notes/{id}/\`         | GET    | Retrieve note details                    |
| \`/api/notes/{id}/\`         | PUT    | Update note content/links                |
| \`/api/notes/{id}/\`         | DELETE | Delete a note                            |

## Getting Started

### Prerequisites
- Python 3.11+  
- Node.js 18.x & npm  
- PostgreSQL 14+  
- Redis  
- FFmpeg  

### Installation

\`\`\`bash
git clone https://github.com/lucifron28/scrybesync.git
cd scrybesync/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
\`\`\`

### Environment Variables

In \`backend/.env\`:

\`\`\`
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:pass@db:5432/scrybesync
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=your_openai_key
\`\`\`

### Running Locally

\`\`\`bash
redis-server
celery -A config worker -l info
python manage.py runserver
\`\`\`

## Docker Setup

\`\`\`bash
docker-compose up --build
\`\`\`

## Frontend Setup

\`\`\`bash
cd ../frontend
npm install
npm run dev
\`\`\`

Access at `http://localhost:3000`

## Contributing

1. Fork the repo  
2. Create a feature branch (\`git checkout -b feature/foo\`)  
3. Commit your changes (\`git commit -am "Add foo"\`)  
4. Push to the branch (\`git push origin feature/foo\`)  
5. Open a Pull Request  

## License

MIT © Your Name
