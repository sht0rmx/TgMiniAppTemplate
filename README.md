# Telegram MiniApp Template

A production-ready template for building Telegram Mini Apps with a FastAPI backend, Vue.js frontend, and a Python Telegram bot. Includes JWT authentication, QR code login, session management, file storage, and real-time updates out of the box.

## Tech Stack

| Layer        | Technology                                                        |
| ------------ | ----------------------------------------------------------------- |
| **Backend**  | FastAPI, SQLAlchemy 2.0 (async), Alembic, PyJWT, APScheduler     |
| **Frontend** | Vue 3 (Composition API, TypeScript), Pinia, Vue Router, Axios     |
| **Bot**      | PyTelegramBotAPI (async)                                          |
| **Database** | PostgreSQL 15                                                     |
| **Cache**    | Redis 7                                                           |
| **Storage**  | MinIO (S3-compatible)                                             |
| **UI**       | Tailwind CSS 4 + DaisyUI, RemixIcon                              |
| **Infra**    | Docker, Docker Compose, Nginx (production)                        |
| **Tooling**  | uv (Python), Vite 7 (frontend), FingerprintJS                    |

## Features

- **Telegram WebApp auth** -- validates `initData` hash, creates user and session
- **QR code login** -- cross-device login with SSE real-time confirmation
- **JWT sessions** -- short-lived access tokens + long-lived refresh tokens (HTTP-only cookies)
- **Device fingerprinting** -- one session per device, tracked via FingerprintJS
- **Session management** -- multiple sessions per user, revocation support
- **Account recovery** -- one-time recovery codes for account transfer
- **Rate limiting** -- Redis-backed per-request rate limiting
- **File storage** -- S3/MinIO integration with per-user file organization
- **Real-time updates** -- SSE for login confirmation, WebSocket for bot updates
- **i18n** -- multilanguage support in both frontend and bot
- **Theming** -- system-aware dark/light themes (default, dim, nord)
- **Maintenance mode** -- frontend flag to freeze all API requests
- **Docker-based workflow** -- dev with hot reload, prod with Nginx

## Project Structure

```
TgMiniAppTemplate/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/routes/         # API endpoints (auth, sessions, ws)
│   │   ├── database/models/    # SQLAlchemy models
│   │   ├── middleware/         # Auth, rate limiting, fingerprinting
│   │   ├── services/           # Business logic
│   │   ├── storage/            # S3/MinIO client
│   │   ├── shemes/             # Pydantic schemas
│   │   └── utils/              # Helpers
│   ├── alembic/                # Database migrations
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
│
├── frontend/                   # Vue 3 frontend
│   ├── src/
│   │   ├── api/                # Axios API layer
│   │   ├── components/         # Vue components
│   │   ├── views/              # Page views
│   │   ├── router/             # Vue Router config
│   │   ├── stores/             # Pinia state stores
│   │   └── locales/            # i18n translations
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
│
├── bot/                        # Telegram bot
│   ├── src/
│   │   ├── handlers/           # Command, callback, inline handlers
│   │   ├── api/                # Backend API client
│   │   ├── utils/              # Logging, messages
│   │   └── locales/            # Bot translations
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
│
├── docker-compose.yml          # Base services (db, redis, minio)
├── docker-compose.dev.yml      # Dev overrides (hot reload, watch)
├── docker-compose.prod.yml     # Prod overrides (restart policies)
├── .env.example                # Root env template (infra credentials)
└── README.md
```

## API Endpoints

All routes are prefixed with `/api/v1`.

| Method | Path                             | Description                     |
| ------ | -------------------------------- | ------------------------------- |
| POST   | `/auth/login/webapp`             | Telegram WebApp login           |
| GET    | `/auth/login/getqr`             | Generate QR code for login      |
| GET    | `/auth/login/search/{id}`       | Check QR login status           |
| GET    | `/auth/login/accept/{id}`       | Accept QR login                 |
| GET    | `/auth/login/by-code/search/{code}` | Search by short code        |
| GET    | `/auth/login/by-code/accept/{code}` | Accept by short code        |
| GET    | `/auth/api-key`                 | Bot API key authentication      |
| GET    | `/auth/check`                   | Verify auth status              |
| GET    | `/auth/token/get-tokens`        | Refresh access token            |
| GET    | `/auth/token/recreate-tokens`   | Create new session              |
| GET    | `/auth/token/revoke`            | Revoke current session          |
| GET    | `/auth/token/recovery`          | Generate recovery code          |
| POST   | `/auth/token/transfer`          | Transfer account via recovery   |
| GET    | `/auth/sse/check/{login_id}`    | SSE stream for login status     |
| GET    | `/session/current`              | Current session info            |
| WS     | `/botupdates/ws`                | WebSocket for bot updates       |

## Prerequisites

- **Docker** and **Docker Compose v2**
- **Git**

For local development without Docker:

- **Python 3.12+** with [uv](https://docs.astral.sh/uv/)
- **Node.js 20.19+** (or 22.12+) with npm
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/sht0rmx/TgMiniAppTemplate.git
cd TgMiniAppTemplate
```

### 2. Configure environment variables

Copy all `.env.example` files and fill in the values:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
cp bot/.env.example bot/.env
```

#### Root `.env`

| Variable            | Description              |
| ------------------- | ------------------------ |
| `POSTGRES_USER`     | PostgreSQL username      |
| `POSTGRES_PASSWORD` | PostgreSQL password      |
| `POSTGRES_DB`       | PostgreSQL database name |
| `MINIO_ROOT_USER`   | MinIO root username      |
| `MINIO_ROOT_PASSWORD` | MinIO root password    |
| `REDIS_PASSWORD`    | Redis password           |

#### `backend/.env`

| Variable              | Description                                           |
| --------------------- | ----------------------------------------------------- |
| `HOST`                | Server host and port (e.g. `0.0.0.0:8000`)           |
| `CORS_ORIGINS`        | Comma-separated allowed origins                       |
| `BOT_TOKEN`           | Telegram bot token from BotFather                     |
| `JWT_SECRET`          | Secret for JWT access tokens                          |
| `LOGIN_SECRET`        | Secret for login codes                                |
| `REFRESH_SECRET`      | Secret for refresh tokens                             |
| `RECOVERY_SECRET`     | Secret for recovery codes                             |
| `API_SECRET`          | Secret for API key generation                         |
| `API_TOKEN_HASH`      | Hashed API token (starts with `sk_`)                  |
| `DATABASE_URL`        | Async PostgreSQL URL (`postgresql+asyncpg://...`)     |
| `S3_REGION`           | MinIO/S3 region                                       |
| `S3_ENDPOINT`         | MinIO/S3 endpoint URL                                 |
| `S3_KEY_ID`           | MinIO/S3 access key                                   |
| `S3_SECRET_ACCESS_KEY`| MinIO/S3 secret key                                   |
| `S3_BUCKET`           | MinIO/S3 bucket name                                  |
| `LOGIN_EXPIRE`        | Login code expiration (e.g. `5m`)                     |
| `ACCESS_EXPITRE`      | Access token expiration (e.g. `30m`)                  |
| `REFRESH_EXPIRE`      | Refresh token expiration (e.g. `60d`)                 |

#### `frontend/.env`

| Variable                 | Description                                    |
| ------------------------ | ---------------------------------------------- |
| `VITE_APP_TITLE`         | App title shown in the browser tab             |
| `VITE_API_URL`           | Backend API base URL                           |
| `VITE_TG_MINIAPP_START`  | Telegram bot miniapp start link                |
| `VITE_CONSTRUCTION_MODE` | `true` to freeze all API requests              |

#### `bot/.env`

| Variable          | Description                         |
| ----------------- | ----------------------------------- |
| `BOT_TOKEN`       | Telegram bot token from BotFather   |
| `API_ENDPOINT`    | Backend API endpoint URL            |
| `API_KEY`         | API key for backend authentication  |
| `TG_STARTAPP_URL` | Telegram miniapp start URL          |

### 3. Run with Docker

**Development** (with hot reload and watch mode):

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up frontend backend --watch --build
```

**Production**:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up frontend backend --build
```

### 4. Set up Telegram

1. Create a bot via [@BotFather](https://t.me/BotFather) and obtain the API token
2. Configure the Mini App button in BotFather with your frontend URL
3. Paste the bot token into `backend/.env` and `bot/.env`

## Local Development (without Docker)

If you prefer to run services directly:

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

> You will still need PostgreSQL, Redis, and MinIO running (either locally or via `docker compose up db redis minio`).

## Docker Services

| Service      | Image / Build     | Port(s)       | Description                |
| ------------ | ----------------- | ------------- | -------------------------- |
| `db`         | `postgres:15`     | 5432          | PostgreSQL database        |
| `redis`      | `redis:7`         | 6379          | Cache and rate limiting    |
| `minio`      | `minio/minio`     | 9000, 9001    | S3-compatible file storage |
| `backend`    | `./backend`       | 8000          | FastAPI API server         |
| `bot`        | `./bot`           | --            | Telegram bot               |
| `frontend`   | `./frontend`      | 5173          | Vue.js dev / Nginx prod    |

## Authors

Created by [@sht0rmx](https://github.com/sht0rmx) with help from [@dima0409](https://github.com/dima0409), 2026.

## License

This project is provided as a template. See the repository for license details.
