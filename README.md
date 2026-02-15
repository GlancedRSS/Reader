<div align="center">

# Glanced Reader

A modern, self-hosted RSS/Atom feed reader.

[![CI](https://github.com/glancedrss/reader/actions/workflows/ci.yml/badge.svg)](https://github.com/glancedrss/reader/actions/workflows/ci.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/glanced/reader)](https://hub.docker.com/r/glanced/reader)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

</div>

![Screenshot](./screenshot-light.webp#gh-light-mode-only)
![Screenshot](./screenshot-dark.webp#gh-dark-mode-only)

## Features

- **Self-hosted**: Full control over your data, runs on your hardware
- **Auto-refresh**: Feeds update automatically, no manual checking
- **Folders & tags**: Organize your reading your way
- **OPML import/export**: Bring your feeds from other readers, leave when you want
- **Full-text search**: Find articles across all your feeds instantly

## Quick Start

```bash
git clone https://github.com/glancedrss/reader.git
cd reader
docker compose up -d
```

The app will be available at `http://localhost:2077`.

## Deployment

### Option 1: Docker Compose (Recommended)

Standard multi-container setup with PostgreSQL, Redis, and app services. Everything included, runs out of the box.

**Services:**
- `db` - PostgreSQL 17
- `redis` - Redis 8 with persistence
- `frontend` - Next.js app (port 2077)
- `backend` - FastAPI server (port 2076)
- `worker` - Background feed refresh

```bash
docker compose up -d
```

**Optional environment variables** (create a `.env` file to customize):

| Variable                        | Default    | Description                |
| ------------------------------- | ---------- | -------------------------- |
| `POSTGRES_PASSWORD`             | `changeme` | PostgreSQL password        |
| `COOKIE_SECURE`                 | `true`     | Set secure flag on cookies |
| `FEED_REFRESH_INTERVAL_MINUTES` | `30`       | Feed refresh interval      |

Image available on [Docker Hub](https://hub.docker.com/r/glanced/reader).

### Option 2: Bundled Container

Single container running all app services (frontend, backend, worker). Requires external PostgreSQL and Redis.

Best for:
- Existing PostgreSQL/Redis infrastructure
- Single-container workflows

```bash
docker run -d \
  --name glanced-reader \
  -p 2077:2077 \
  -v $(pwd)/data:/data \
  -e DATABASE_URL=postgresql://user:pass@host:5432/reader \
  -e REDIS_URL=redis://host:6379 \
  glanced/reader:bundled
```

**Environment variables:**

| Variable                        | Required | Default    | Description                         |
|---------------------------------|----------|------------|-------------------------------------|
| `DATABASE_URL`                  | Yes      | -          | PostgreSQL connection string        |
| `REDIS_URL`                     | Yes      | -          | Redis connection string             |
| `COOKIE_SECURE`                 | No       | `true`     | Set secure flag on cookies (HTTPS)   |
| `FEED_REFRESH_INTERVAL_MINUTES` | No       | `30`       | Feed refresh interval                |

## Development

### Prerequisites

- Python 3.13+
- Node.js 24+
- PostgreSQL 17
- Redis

### Running Locally

```bash
make dev          # Show commands to start all services
```

Then run in separate terminals:

```bash
make backend-dev  # FastAPI backend on port 2076
make worker-dev   # Background worker for feed refresh
make app-dev      # Next.js frontend on port 2077
```

### Code Quality

```bash
make lint         # Run linters (ruff, eslint)
make format       # Format code (ruff format, prettier)
make test         # Run tests
```

### Database Migrations

```bash
make db-make-migration MSG='description'  # Create new migration
make db-upgrade                           # Run migrations
make db-downgrade                         # Revert last migration
make db-current                           # Show current version
```

## Architecture

The backend follows clean architecture principles:

- **Routers**: HTTP endpoints, request validation
- **Application**: Use case orchestration
- **Domain**: Business rules, validation
- **Infrastructure**: Database, cache, external services

## Tech Stack

**Frontend**

- Next.js 15, React 19, TypeScript
- Tailwind CSS v4
- SWR for data fetching, Zustand for state

**Backend**

- FastAPI, Python 3.13+
- SQLAlchemy 2.0 (async)
- PostgreSQL 17, Redis
- Arq for background jobs
