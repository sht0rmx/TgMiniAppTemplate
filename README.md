# Telegram Mini App Template
A production-ready starter kit for Telegram Mini Apps. It features a FastAPI backend, Vue.js frontend, and Python Telegram bot with JWT auth, QR login, file storage, and real-time updates.
## Tech Stack
| Layer     | Technology                                      |
|-----------|-------------------------------------------------|
| Backend   | FastAPI, SQLAlchemy 2.0 (async), Alembic, PyJWT, APScheduler |
| Frontend  | Vue 3 (Composition API, TypeScript), Pinia, Vue Router, Axios |
| Bot       | PyTelegramBotAPI (async)                        |
| Database  | PostgreSQL 15                                   |
| Cache     | Redis 7                                         |
| Storage   | MinIO (S3-compatible)                           |
| UI        | Tailwind CSS 4 + DaisyUI, RemixIcon             |
| Infra     | Docker, Docker Compose, Nginx (prod)            |
| Tooling   | uv (Python), Vite 7, FingerprintJS              |
## Key Features
- Telegram WebApp authentication validates `initData` and manages user sessions.
- QR code login enables cross-device access with SSE for real-time status.
- JWT sessions use short-lived access tokens and HTTP-only refresh cookies.
- Device fingerprinting via FingerprintJS limits one session per device.
- Full session controls including revocation and multi-session support.
- Account recovery with one-time codes for secure transfers.
- Redis-based rate limiting and S3/MinIO file storage per user.
- Real-time SSE/WebSocket updates, i18n, theming, and maintenance mode.
- Docker workflows for dev (hot reload) and production.
## Project Structure
```
TgMiniAppTemplate/
├── backend/           # FastAPI API, models, services
│   ├── app/
│   │   ├── api/routes/
│   │   ├── database/models/
│   │   ├── middleware/
│   │   ├── services/
│   │   ├── storage/
│   │   ├── schemas/
│   │   └── utils/
│   ├── alembic/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
├── frontend/          # Vue 3 app
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── views/
│   │   ├── router/
│   │   ├── stores/
│   │   └── locales/
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
├── bot/               # Telegram bot handlers
│   ├── src/
│   │   ├── handlers/
│   │   ├── api/
│   │   ├── utils/
│   │   └── locales/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .env.example
└── README.md
```
## API Endpoints
All under `/api/v1`.

| Method | Path                              | Purpose                  |
|--------|-----------------------------------|--------------------------|
| POST   | `/auth/login/webapp`             | WebApp login             |
| GET    | `/auth/login/getqr`              | Generate QR              |
| GET    | `/auth/login/search/{id}`        | Poll QR status           |
| GET    | `/auth/login/accept/{id}`        | Confirm QR login         |
| GET    | `/auth/login/by-code/search/{code}` | Check recovery code |
| GET    | `/auth/login/by-code/accept/{code}` | Use recovery code  |
| GET    | `/auth/api-key`                  | Bot API auth             |
| GET    | `/auth/check`                    | Auth status              |
| GET    | `/auth/token/get-tokens`         | Refresh tokens           |
| GET    | `/auth/token/recreate-tokens`    | New session              |
| GET    | `/auth/token/revoke`             | Revoke session           |
| GET    | `/auth/token/recovery`           | Generate recovery code   |
| POST   | `/auth/token/transfer`           | Transfer via recovery    |
| GET    | `/auth/sse/check/{login_id}`     | SSE login updates        |
| GET    | `/session/current`               | Session details          |
## Prerequisites
- Docker and Docker Compose v2
- Git

Local dev needs:
- Python 3.12+ with uv
- Node.js 20.19+ or 22.12+
- Telegram bot token from @BotFather
- Yandex Oauth token
## Quick Start
### Clone Repo
```bash
git clone https://github.com/sht0rmx/TgMiniAppTemplate.git
cd TgMiniAppTemplate
```
### Environment Setup
run `./install.sh` and select generate env files
### Docker Dev Mode
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up frontend backend bot --watch --build
```
### Docker Prod Mode
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```
### Telegram Setup
1. Create bot via @BotFather, get token.
2. Set Mini App URL in BotFather.
3. Add token to backend/bot `.env` files. [github](https://github.com/indmdev/Telegram-Store-MiniApp)
## Local Dev (No Docker)
Run DB/Redis/MinIO via `docker compose up db redis minio`.

**Backend:**
```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Bot:**
```bash
cd bot
uv sync
uv run python src/main.py
```
## Services Overview
| Service   | Ports     | Role                      |
|-----------|-----------|---------------------------|
| db        | 5432      | PostgreSQL                |
| redis     | 6379      | Caching/rate limits       |
| minio     | 9000/9001 | File storage              |
| backend   | 8000      | API server                |
| frontend  | 5173      | Vue dev/Nginx prod        |
| bot       | -         | Telegram handler          |
## Author
[@sht0rmx](https://github.com/sht0rmx)