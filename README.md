# InboxZero

A full-stack app made up of:

- **`api/`** — backend, [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **`ui/app/`** — frontend, [Next.js](https://nextjs.org/) (React + TypeScript)
- **PostgreSQL** — primary database
- **Redis** — asynchrone queue

## Project structure

```
.
├── api/                 # FastAPI backend
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── ui/
│   ├── app/             # Next.js frontend
│   └── Dockerfile
├── docker-compose.yaml  # orchestrates ui, api, postgres, redis
├── .env.example         # template for required environment variables
└── .env                 # your local config, git-ignored
```

## Prerequisites

- Git
- A copy of the env file: `cp .env.example .env`, then fill in real values if you change the defaults.

---

## Run with Docker Compose

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose v2 (`docker compose version`)

### 1. Create your env file if you haven't already:

   ```bash
   cp .env.example .env
   ```

### 2. Build and start everything:

    ```bash
    docker compose up --build
    ```

This starts 4 containers: `ui` (port 3000), `api` (port 8000), `postgres` (port 5432), `redis` (port 6379). `api` waits for Postgres and Redis to pass their healthchecks before starting.

**Note:** the `api` and `ui` Dockerfiles currently default to `CMD ["sleep", "infinity"]`. A dev-container style placeholder, that starts container and keep it active but never starts service inside. To start service incide:

    ```bash
     docker compose exec api uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
     docker compose exec ui pnpm dev
    ```

### 3. Visit:
   - UI: http://localhost:3000
   - API health check: http://localhost:8000/health

### 4. Stop everything:

   ```bash
   docker compose down
   ```

---

## Run locally, without Docker (ignoring the Dockerfiles)

### Prerequisites

- Python 3.13+ (the Dockerfile pins `python:3.15-rc-bookworm`; any recent 3.x works locally)
- Node.js 20+
- pnpm (`npm install -g pnpm`)
- PostgreSQL running locally
- Redis running locally

### 1. Create your env file if you haven't already:

   ```bash
   cp .env.example .env
   ```

### 2. Databases

Install and start Postgres and Redis with your OS package manager, e.g. on macOS:

```bash
brew install postgresql redis
brew services start postgresql
brew services start redis
```

### 3. Backend (API)

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check it's up: http://localhost:8000/health

### 4. Frontend (UI)

```bash
cd ui/app
pnpm install
pnpm dev
```

Visit: http://localhost:3000

---

## Ports reference

| Service  | Port | URL                           |
|----------|------|-------------------------------|
| ui       | 3000 | http://localhost:3000         |
| api      | 8000 | http://localhost:8000/health  |
| postgres | 5432 | —                             |
| redis    | 6379 | —                             |
