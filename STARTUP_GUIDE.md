# Vietnamese Legal Chatbot RAG System — Startup Guide

## Prerequisites

- **Docker** and **Docker Compose** installed
- **API Keys** ready:
  - `GEMINI_API_KEY` — Google Gemini API key
  - `COHERE_API_KEY` — Cohere reranking key
  - `TAVILY_API_KEY` — Tavily web search key
- Ports available: **3308**, **6333**, **6334**, **6379**, **8000**, **8051**

---

## 1. Create the Docker Network

All services communicate over a shared external network. Create it once before starting anything:

```bash
docker network create internal-network
```

---

## 2. Start the Database

```bash
cd database
```

### 2.1 Configure environment

Copy the template and set your MariaDB root password:

```bash
cp .env.template .env
```

Edit `.env`:

```env
MYSQL_ROOT_PASSWORD=your_secure_password
```

> **Important:** Do NOT wrap values in quotes. Docker passes quote characters literally, causing authentication failures.

### 2.2 Start MariaDB

```bash
docker compose up -d
```

This starts **MariaDB 11.5.1** on port `3308` (mapped from container port `3306`) and runs `init.sql` to create the `demo_bot` database on first launch.

Wait a few seconds for MariaDB to initialize before proceeding.

---

## 3. Start Redis

The backend requires a Redis instance at `redis:6379` for Celery task queuing. If you don't already have one running:

```bash
docker run -d --name redis --network internal-network -p 6379:6379 redis:latest
```

If you already have a Redis container, make sure it is attached to `internal-network`:

```bash
docker network connect internal-network redis
```

---

## 4. Start the Backend

```bash
cd backend
```

### 4.1 Configure environment

Copy the template and fill in your API keys and database password:

```bash
cp .env.template .env
```

Edit `.env`:

```env
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_HOST=mariadb-tiny
MYSQL_PORT=3306

CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379

COHERE_API_KEY=your_cohere_key
GEMINI_API_KEY=your_gemini_key
TAVILY_API_KEY=your_tavily_key

VIETNAMESE_LLM_API_URL=http://3.90.175.145:6000/v1/chat/completions
```

> **Important:**
> - `MYSQL_ROOT_PASSWORD` must match the value in `database/.env`.
> - `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` must point to your Redis container hostname (e.g. `redis` or `valkey-db`).
> - Do NOT use quotes around values.

### 4.2 Start backend services

```bash
docker compose up -d --build
```

This starts three containers:

| Container | Description | Port |
|---|---|---|
| `chatbot-api` | FastAPI server (2 Uvicorn workers) | `8000` |
| `chatbot-worker` | Celery worker for async tasks | — |
| `qdrant-db` | Qdrant vector database | `6333`, `6334` |

### 4.3 Verify

```bash
docker logs chatbot-api --tail 20
```

You should see:

```
Application startup complete
Agent initialized with 8 tools
```

You can also hit the health endpoint:

```bash
curl http://localhost:8000/health
```

---

## 5. Start the Frontend

```bash
cd frontend
docker compose up -d --build
```

This starts the **Streamlit** chat interface.

| Container | Description | Port |
|---|---|---|
| `chatbot-ui` | Streamlit web UI | `8051` |

Open **http://localhost:8051** in your browser.

---

## 6. (Optional) Start Monitoring

```bash
cd monitoring
docker compose up -d
```

| Container | Description | Port |
|---|---|---|
| `legal-chatbot-prometheus` | Prometheus metrics | `9090` |
| `legal-chatbot-grafana` | Grafana dashboards | `3000` |
| `legal-chatbot-node-exporter` | System metrics | `9100` |
| `legal-chatbot-cadvisor` | Container metrics | `8080` |
| `legal-chatbot-blackbox` | HTTP endpoint monitoring | — |

Default Grafana login: `admin` / `admin123`

---

## 7. (Optional) Start Embedding Serving

```bash
cd embed_serving
docker compose -f docker-compose.serving.yml up -d --build
```

| Container | Description | Port |
|---|---|---|
| `legal-embedding-api` | BGE-M3 embedding API | `5000` |

---

## Startup Order Summary

```
1. docker network create internal-network
2. database/         →  docker compose up -d
3. Redis             →  docker run ... (if not already running)
4. backend/          →  docker compose up -d --build
5. frontend/         →  docker compose up -d --build
6. monitoring/       →  docker compose up -d          (optional)
7. embed_serving/    →  docker compose up -d --build  (optional)
```

---

## Shutdown

Reverse order:

```bash
cd frontend    && docker compose down
cd backend     && docker compose down
cd database    && docker compose down
cd monitoring  && docker compose down   # if running
```

To also delete database data (full reset):

```bash
cd database && docker compose down -v
```

---

## Troubleshooting

### Network not found: `internal-network`

```
Error: network internal-network declared as external, but could not be found
```

**Fix:** Create it manually:

```bash
docker network create internal-network
```

---

### `entrypoint.sh: not found` or `exec format error`

Caused by Windows CRLF line endings in shell scripts. Linux containers require LF.

**Fix (PowerShell):**

```powershell
# Backend
(Get-Content backend/entrypoint.sh -Raw) -replace "`r`n", "`n" | Set-Content backend/entrypoint.sh -NoNewline -Encoding utf8

# Frontend
(Get-Content frontend/entrypoint.sh -Raw) -replace "`r`n", "`n" | Set-Content frontend/entrypoint.sh -NoNewline -Encoding utf8
```

Then rebuild:

```bash
docker compose up -d --build
```

**Prevention:** Configure Git to preserve LF for shell scripts. Add to `.gitattributes`:

```
*.sh text eol=lf
```

---

### MariaDB: `Access denied for user 'root'`

**Cause 1 — Quotes in `.env`:**

```env
# WRONG
MYSQL_ROOT_PASSWORD='my_password'

# CORRECT
MYSQL_ROOT_PASSWORD=my_password
```

**Cause 2 — Password changed after initial volume creation:**

The MariaDB root password is set only on first startup. If you change the password in `.env` after the volume exists, the old password persists.

**Fix:** Delete the volume and recreate:

```bash
cd database
docker compose down -v
docker compose up -d
```

> **Warning:** This deletes all database data.

---

### Port 6379 already in use (Redis conflict)

```
Bind for 0.0.0.0:6379 failed: port is already allocated
```

Another Redis (or Valkey) container is already using port 6379.

**Fix:** Use the existing container. Update `backend/.env` to point to its hostname:

```env
CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379
```

Make sure the existing Redis container is on the `internal-network`:

```bash
docker network connect internal-network redis
```

---

### Port 3308 already in use (MariaDB conflict)

**Fix:** Either stop the conflicting service, or change the host port in `database/docker-compose.yml`:

```yaml
ports:
  - "3309:3306"   # change 3308 to any free port
```

---

### Backend cannot connect to MariaDB

Check that:

1. `mariadb-tiny` container is running: `docker ps | grep mariadb`
2. `MYSQL_HOST=mariadb-tiny` in `backend/.env`
3. `MYSQL_ROOT_PASSWORD` matches between `database/.env` and `backend/.env`
4. Both containers are on `internal-network`: `docker network inspect internal-network`

---

### Backend cannot connect to Qdrant

Qdrant starts with the backend in the same compose file, so it should be on the same network. If the backend starts before Qdrant is ready, it will retry automatically.

If issues persist, check:

```bash
docker logs qdrant-db --tail 20
curl http://localhost:6333/healthz
```

---

### Celery worker not processing tasks

```bash
docker logs chatbot-worker --tail 30
```

Common causes:

- Redis is not reachable — check `CELERY_BROKER_URL` in `.env`
- Redis container is not on `internal-network`

---

### Frontend shows "Backend not available"

The frontend connects to the backend at `http://chatbot-api:8000` over the Docker network.

1. Confirm `chatbot-api` is running and healthy
2. Confirm both `chatbot-ui` and `chatbot-api` are on `internal-network`
3. Check backend logs: `docker logs chatbot-api --tail 20`

---

### Docker Compose "version is obsolete" warning

```
WARN[0000] ... version is obsolete
```

This is cosmetic and harmless. Modern Docker Compose ignores the `version` field. You can safely remove the `version: '3.8'` line from all compose files if desired.

---

### Rebuild after code changes

If you modify source code, rebuild the affected container:

```bash
docker compose up -d --build
```

For backend-only changes where volumes are mounted (`- .:/usr/src/app/`), a simple restart may suffice:

```bash
docker compose restart chatbot-api chatbot-worker
```
