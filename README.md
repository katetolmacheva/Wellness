# Wellness / Health Article Platform

### Это платформа для публикации и модерации статей о здоровье:
- Next.js фронтенда;
- Node.js/Express бэкенда с Prisma и PostgreSQL;
- Python-скриптов для импорта RSS и обработки картинок;
- FastAPI чат‑сервиса (с интеграцией GROQ/OpenAI) для модерации и верификации экспертов.

### Ключевые сценарии
- Публикация статей: только верифицированные эксперты. Перед публикацией статья проходит автоматическую модерацию.
- RSS‑импорт: backend/scripts/rss_importer.py парсит ленты новостей, формирует контент, скачивает изображения и сохраняет в БД.
- Верификация экспертов: backend/chatbot/chat_app.py принимает файл диплома, рендерит страницы (PyMuPDF) и отправляет на LLM для проверки.
- Чат-ассистент: FastAPI + GROQ для диалогов, генерации коротких заголовков и модерации статей.
- Скрипты поддержки.

### Стек
- Frontend: Next.js (React)
- Backend: Node.js, Express, Prisma (Postgres)
- RSS/import: Python (feedparser, BeautifulSoup, requests)
- Чат/модерация: FastAPI, Groq/OpenAI, PyMuPDF
- База данных: PostgreSQL

### Главные файлы и папки
- frontend: Next.js (course_project_3)
- backend/src — Express контроллеры и роуты (articles, profile и т.д.)
- backend/scripts — rss_importer.py, rss_utils.py, утилиты по картинкам
- backend/chatbot — FastAPI / логика модерации и верификации
- backend/prisma — schema.prisma, seed.js
- public/uploads, public/images — хранение загруженных обложек и картинок статей

### Переменные окружения
Общие: 
- PORT
- HOST
- DATABASE_URL

Флаги запуска и отладки:
- SEED_DB_ON_START=false   # true|false — запуск seed при старте (dev only)
- DEBUG_AUTH_NO_EMAIL=false # true|false — пропуск валидации email в dev

Адрес сервиса модерации/чатбота (FastAPI)
- CHATBOT_URL

GROQ ключ
- GROQ_API_KEY

Brevo (провайдер email)
- BREVO_API_KEY
- SMTP_HOST
- SMTP_PORT
- SMTP_SECURE
- SMTP_USER
- SMTP_PASS
- SMTP_FROM

### Быстрый запуск локально
- Frontend:
  - В корне фронтенда: npm install && npm run dev
  - http://localhost:3000

- Backend (через Docker):
  1. В корне проекта backend подготовить файл .env
  2. Запуск через docker:
     - cd backend
     - docker compose up

- Chatbot:
  - cd backend/chatbot && pip install -r requirements.txt && uvicorn chat_app:app --host 0.0.0.0 --port 8000


Примечание о продакшене
- Backend и chatbot на Reilway 
- Frontend на Vercel
