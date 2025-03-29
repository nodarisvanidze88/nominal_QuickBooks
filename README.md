# 📦 Nominal: OAuth-based QuickBooks API Integration

## 🚀 Overview

**Nominal** is a backend system built with FastAPI and Docker that integrates with the QuickBooks Online API using OAuth 2.0. It allows secure token handling, periodic syncing of account data from QuickBooks, and provides endpoints for account querying and token management.

---

## ✨ Features

-   🔐 OAuth 2.0-based secure token management
-   🔁 Automatic token refresh logic
-   ⏰ Scheduled background jobs using Celery and Celery Beat
-   🐳 Fully Dockerized architecture (API, PostgreSQL, Redis, Worker, Beat)
-   🔍 RESTful API to search and retrieve QuickBooks accounts
-   🧬 Database migrations with Alembic
-   📡 Centralized logging with Loggly

---

## 🧰 Tech Stack

-   **FastAPI** – REST API framework
-   **SQLAlchemy** – ORM for DB access
-   **PostgreSQL** – Primary database
-   **Redis** – Broker for Celery
-   **Celery** – Background task queue
-   **Alembic** – Schema migrations
-   **Docker** – Container orchestration
-   **Loggly** – Logging service

---

## 🔐 QuickBooks OAuth Integration

This app uses [QuickBooks OAuth 2.0](https://developer.intuit.com/app/developer/qbo/docs/get-started) to authenticate with the QuickBooks API and fetch accounts. Tokens are securely stored and reused for scheduled tasks or manual triggers.

---

## 📁 Project Structure

```bash
Nominal/
│
├── alembic/               # Alembic migration scripts
├── core/                  # Configuration loading
├── database/              # DB session and base
├── models/                # SQLAlchemy ORM models
├── routes/                # FastAPI route handlers
├── schemas/               # Pydantic validation schemas
├── services/              # Logic for OAuth and account sync
├── tasks/                 # Celery tasks
├── tests/                 # Unit tests
├── utils/                 # Logging utils, etc.
├── .env.example           # Sample environment config
├── main.py                # App entrypoint
├── Dockerfile             # Image instructions
├── docker-compose.yml     # Multi-container services
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## ⚙️ Setup with Docker (Recommended for Windows/Linux)

### ✅ Prerequisites

-   Docker
-   Docker Compose

---

### 📥 [1. Clone the Repository](#📥-1-clone-the-repository)

```bash
git clone <repo-url>
cd nominal_QuickBooks
```

---

### 🔐 [2. Configure Environment](#🔐-2-configure-environment)

Copy and edit the `.env` file:

```bash
cp .env.example .env
```

🧾 Example `.env`:

```ini
POSTGRES_DB=nominal
POSTGRES_USER=db_user
POSTGRES_PASSWORD=db_password

CLIENT_ID=your_qbo_client_id
CLIENT_SECRET=your_qbo_client_secret
REDIRECT_URI=http://localhost:8000/callback

DATABASE_URL_LOCAL=postgresql://db_user:db_password@localhost:5432/nominal
DATABASE_URL_DOCKER=postgresql://db_user:db_password@db:5432/nominal
DATABASE_URL_LAPTOP=postgresql://user:pass@host:5432/dbname

ENVIRONMENT=development
USE_DOCKER=true
USE_LAPTOP=false

LOGGLY_TOKEN=your-loggly-token

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_USERNAME=
REDIS_PASSWORD=

CELERY_SCHEDULE_INTERVAL=600
```

---

### 🐳 3. Run with Docker

```bash
docker-compose down -v  # Optional: clean previous state
docker-compose up --build
```

What this does:

-   🔧 Installs dependencies
-   ⛓️ Runs Alembic migrations
-   ✅ Runs unit tests
-   🚀 Launches API + Celery Worker + Celery Beat

---

### 🌐 Access the API

```bash
http://localhost:8000
```

---

## ⚙️ Setup Locally (Without Docker)

### 1. Clone the Repository

```bash
git clone <repo-url>
cd nominal_QuickBooks
```

### 2. Create Environment

```bash
cp .env.example .env
```

### 3. Create Virtual Environment

```bash
# Windows
python -m venv venv

# Linux/macOS
python3 -m venv venv
```

### 4. Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Create Database

Ensure PostgreSQL is running and you’ve created the `nominal` database.

### 7. Run Migrations

```bash
alembic upgrade head
```

### 8. Run Tests

```bash
pytest tests/
```

### 9. Run the API Server

```bash
uvicorn main:app --reload
```

### 10. Run Celery Worker

```bash
celery -A tasks.tasks worker --pool=solo --loglevel=info
```

### 11. Run Celery Beat

```bash
celery -A tasks.tasks beat --loglevel=info
```

---

## 🔌 API Endpoints

| Method | Endpoint            | Description                            |
| ------ | ------------------- | -------------------------------------- |
| GET    | `/`                 | Initiate QuickBooks OAuth login        |
| GET    | `/callback`         | Handle redirect from QuickBooks        |
| GET    | `/accounts`         | Manually trigger account sync          |
| GET    | `/accounts/search`  | Search accounts                        |
| GET    | `/accounts/summary` | Show summary result by classification  |
| GET    | `/accounts/tree`    | Generate tree child/parent of accounts |
| GET    | `/health`           | Health check                           |

---

## 🪵 Logging

Log messages are sent to **Loggly** (if `LOGGLY_TOKEN` is set).

-   `celery.task` → for Celery logs
-   `fastapi.middleware` → for HTTP logs

---

## 🧹 Cleanup Tips

To remove all containers, volumes, and images:

```bash
docker-compose down -v --remove-orphans
```

To fully rebuild:

```bash
docker-compose down -v
docker-compose up --build
```

---

## 🧠 Additional Notes

-   Redis is required for Celery to function
-   Celery Beat will run scheduled jobs (e.g., syncing accounts)
-   Loggly setup requires a valid token from [Loggly](https://www.loggly.com/)
-   PostgreSQL data is stored in a Docker volume (`pgdata`) for persistence
