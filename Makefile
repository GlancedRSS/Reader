.PHONY: help setup dev backend-dev worker-dev app-dev test lint format db-make-migration db-upgrade db-downgrade db-stamp db-current db-history db-dump docker docker-bundled clean

# Default target
help:
	@echo "Glanced Reader Development"
	@echo ""
	@echo "🚀 Setup:"
	@echo "  setup        - Install dependencies and configure environment"
	@echo ""
	@echo "Quick Start:"
	@echo "  dev          - Show commands to start all services"
	@echo ""
	@echo "Services:"
	@echo "  backend-dev  - Start FastAPI server (port 2076)"
	@echo "  worker-dev   - Start Arq background worker"
	@echo "  app-dev      - Start Next.js app (port 2077)"
	@echo ""
	@echo "🗄️  Database (Alembic):"
	@echo "  db-make-migration - Create new Alembic migration from model changes"
	@echo "  db-upgrade        - Run Alembic migrations to latest"
	@echo "  db-downgrade      - Revert last Alembic migration"
	@echo "  db-stamp          - Stamp database with revision (for existing DBs)"
	@echo "  db-current        - Show current migration version"
	@echo "  db-history        - Show migration history"
	@echo "  db-dump           - Dump database schema"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linters"
	@echo "  format       - Format code"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean        - Clean generated files"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker       - Build standard Docker image"
	@echo "  docker-bundled - Build bundled Docker image"

# Setup
setup:
	@echo "🚀 Setting up development environment..."
	@echo ""
	@echo "📦 Backend (Python)..."
	@if [ ! -d "server" ]; then \
		echo "❌ server directory not found"; \
		exit 1; \
	fi
	@if [ ! -d "server/.venv" ]; then \
		echo "  Creating Python virtual environment..."; \
		cd server && python3 -m venv .venv; \
	fi
	@echo "  Installing Python dependencies..."
	@cd server && .venv/bin/pip install --upgrade pip -q && .venv/bin/pip install -e . -q
	@if [ ! -f "server/.env" ]; then \
		echo "  Copying server/.env.example to server/.env"; \
		cp server/.env.example server/.env; \
		echo "  ⚠️  Edit server/.env with your database and Redis URLs"; \
	fi
	@echo ""
	@echo "📦 Frontend (Node.js)..."
	@if [ ! -d "app" ]; then \
		echo "❌ app directory not found"; \
		exit 1; \
	fi
	@if [ ! -d "app/node_modules" ]; then \
		echo "  Installing Node dependencies..."; \
		cd app && npm install; \
	fi
	@if [ ! -f "app/.env.local" ]; then \
		echo "  Copying app/.env.local.example to app/.env.local"; \
		cp app/.env.local.example app/.env.local; \
		echo "  ⚠️  Edit app/.env.local with NEXT_PUBLIC_API_URL"; \
	fi
	@echo ""
	@echo "🪝 Git hooks..."
	@if command -v pre-commit > /dev/null 2>&1; then \
		pre-commit install > /dev/null 2>&1 || true; \
		pre-commit install --hook-type commit-msg > /dev/null 2>&1 || true; \
		pre-commit install --hook-type pre-push > /dev/null 2>&1 || true; \
		echo "  pre-commit hooks installed"; \
	else \
		echo "  ⚠️  pre-commit not found. Run: pip install pre-commit"; \
	fi
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "🚀 Next steps:"
	@echo "  1. Edit server/.env and app/.env.local with your configuration"
	@echo "  2. Run 'make dev' to see commands to start services"

# Development
dev:
	@echo "🚀 Starting development environment..."
	@echo ""
	@echo "Terminal 1 - FastAPI Server:"
	@echo "  make backend-dev"
	@echo ""
	@echo "Terminal 2 - Arq Worker:"
	@echo "  make worker-dev"
	@echo ""
	@echo "Terminal 3 - Next.js App:"
	@echo "  make app-dev"

backend-dev:
	@echo "🐍 Starting FastAPI server..."
	@if [ ! -d "server" ]; then \
		echo "❌ server directory not found"; \
		exit 1; \
	fi
	@if [ ! -d "server/.venv" ]; then \
		echo "❌ venv not found. Run: cd server && python3 -m venv .venv && .venv/bin/pip install -e ."; \
		exit 1; \
	fi
	@echo "   API: http://localhost:2076"
	@echo "   Docs: http://localhost:2076/docs"
	@echo ""
	cd server && .venv/bin/python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 2076

worker-dev:
	@echo "⚙️  Starting Arq worker..."
	@if [ ! -d "server" ]; then \
		echo "❌ server directory not found"; \
		exit 1; \
	fi
	@if [ ! -d "server/.venv" ]; then \
		echo "❌ venv not found. Run: cd server && python3 -m venv .venv && .venv/bin/pip install -e ."; \
		exit 1; \
	fi
	@echo "   Arq Worker (processes background jobs)"
	@echo ""
	cd server && .venv/bin/arq backend.workers.settings.WorkerSettings

app-dev:
	@echo "⚛️  Starting Next.js app..."
	@if [ ! -d "app" ]; then \
		echo "❌ app directory not found"; \
		exit 1; \
	fi
	@echo "   App: http://localhost:2077"
	@echo ""
	cd app && npm run dev

# Database (Alembic)
db-make-migration:
	@echo "🔨 Creating new Alembic migration..."
	@if [ -z "$$MSG" ]; then \
		echo "❌ MSG not set. Usage: make db-make-migration MSG='add_user_table'"; \
		exit 1; \
	fi
	@if [ ! -d "server/.venv" ]; then \
		echo "❌ venv not found. Run: cd server && python3 -m venv .venv && .venv/bin/pip install -e ."; \
		exit 1; \
	fi
	@cd server && .venv/bin/alembic revision --autogenerate -m "$$MSG"
	@echo "✅ Migration created. Review server/alembic/versions/ and run 'make db-upgrade'"

db-upgrade:
	@echo "⬆️  Running Alembic migrations..."
	@if [ ! -d "server/.venv" ]; then \
		echo "❌ venv not found. Run: cd server && python3 -m venv .venv && .venv/bin/pip install -e ."; \
		exit 1; \
	fi
	@cd server && .venv/bin/alembic upgrade head
	@echo "✅ Migrations complete"

db-downgrade:
	@echo "⬇️  Reverting last migration..."
	@if [ ! -d "server/.venv" ]; then \
		echo "❌ venv not found. Run: cd server && python3 -m venv .venv && .venv/bin/pip install -e ."; \
		exit 1; \
	fi
	@cd server && .venv/bin/alembic downgrade -1
	@echo "✅ Downgrade complete"

db-stamp:
	@echo "📋 Stamping database..."
	@if [ ! -d "server/.venv" ]; then \
		echo "❌ venv not found. Run: cd server && python3 -m venv .venv && .venv/bin/pip install -e ."; \
		exit 1; \
	fi
	@if [ -z "$$REV" ]; then \
		cd server && .venv/bin/alembic stamp head; \
	else \
		cd server && .venv/bin/alembic stamp "$$REV"; \
	fi
	@echo "✅ Database stamped"

db-current:
	@echo "📍 Current migration version:"
	@if [ ! -d "server/.venv" ]; then \
		echo "❌ venv not found. Run: cd server && python3 -m venv .venv && .venv/bin/pip install -e ."; \
		exit 1; \
	fi
	@cd server && .venv/bin/alembic current

db-history:
	@echo "📜 Migration history:"
	@if [ ! -d "server/.venv" ]; then \
		echo "❌ venv not found. Run: cd server && python3 -m venv .venv && .venv/bin/pip install -e ."; \
		exit 1; \
	fi
	@cd server && .venv/bin/alembic history

db-dump:
	@echo "📋 Dumping database schema..."
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "❌ DATABASE_URL not set"; \
		exit 1; \
	fi
	pg_dump "$$DATABASE_URL" --schema-only --no-owner --no-privileges

# Testing
test:
	@echo "🧪 Running tests..."
	@if [ ! -d "server" ]; then \
		echo "❌ server directory not found"; \
		exit 1; \
	fi
	@if [ ! -d "server/.venv" ]; then \
		echo "❌ venv not found. Run: cd server && python3 -m venv .venv && .venv/bin/pip install -e ."; \
		exit 1; \
	fi
	cd server && .venv/bin/python -m pytest -v

lint:
	@echo "🔍 Running linters..."
	@echo "   Backend..."
	@if [ -d "server" ]; then \
		if [ -d "server/.venv" ]; then \
			cd server && .venv/bin/python -m ruff check .; \
		else \
			echo "   ⚠️  venv not found, skipping backend lint"; \
		fi \
	fi
	@echo "   App..."
	@if [ -d "app" ]; then \
		cd app && npx eslint .; \
	fi

format:
	@echo "✨ Formatting code..."
	@echo "   Backend..."
	@if [ -d "server" ]; then \
		if [ -d "server/.venv" ]; then \
			cd server && .venv/bin/python -m ruff format .; \
		else \
			echo "   ⚠️  venv not found, skipping backend format"; \
		fi \
	fi
	@echo "   App..."
	@if [ -d "app" ]; then \
		cd app && npx prettier --write .; \
	fi

# Maintenance
clean:
	@echo "🧹 Cleaning generated files..."
	@find server -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find server -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find server -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf app/.next
	@echo "✅ Clean complete"

# Docker
docker:
	@echo "🐳 Building standard Docker image..."
	docker build -t glanced/reader:latest .

docker-bundled:
	@echo "🐳 Building bundled Docker image..."
	docker build -f Dockerfile.bundled -t glanced/reader:bundled .
