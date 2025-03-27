# QuickBooks Online OAuth Integration

This is a FastAPI-based OAuth 2.0 integration with QuickBooks Online (QBO).

## Features

-   OAuth 2.0 flow using `intuit-oauth`
-   PostgreSQL-based token and account storage
-   Token reuse and refresh support
-   QBO Account data fetch & sync
-   Dockerized for local or cloud deployment
-   Swagger/OpenAPI documentation

---

## Setup

### 1. Clone the repository and navigate into it

```bash
git clone <repo-url>
cd nominal
```

### 2. Setup Environment

```bash
cp .env.example .env
```

Fill in your QuickBooks client credentials and desired database URL.

### 3. Start using Docker

```bash
docker-compose up --build
```

### 4. Run Alembic migrations

```bash
docker-compose exec app alembic upgrade head
```

---

## API Endpoints

### Auth

-   `GET /auth` – Start OAuth
-   `GET /callback` – Handle redirect

### Accounts

-   `GET /accounts` – Fetch and save accounts

### Health

-   `GET /health` – Status check

---

## Testing

Run tests with:

```bash
pytest
```

---

## Example cURL

```bash
curl -X GET http://localhost:8000/accounts
```

---

## Folder Structure

-   `app/routes` – API routers
-   `app/services` – business logic
-   `app/models` – DB models
-   `app/utils` – reusable utilities
-   `app/core` – settings and config
-   `app/tests` – unit tests

---

## Improvements over base task

-   Retry/backoff on QBO requests
-   Logging
-   Parent/child account relationship support
-   Token refresh handling
