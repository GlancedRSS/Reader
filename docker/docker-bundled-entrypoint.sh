#!/bin/sh
set -e

# Validate required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable is required"
    echo "Example: postgresql://user:password@host:5432/database"
    exit 1
fi

if [ -z "$REDIS_URL" ]; then
    echo "Error: REDIS_URL environment variable is required"
    echo "Example: redis://host:6379"
    exit 1
fi

# Set defaults
ENVIRONMENT=${ENVIRONMENT:-production}
COOKIE_SECURE=${COOKIE_SECURE:-true}
STORAGE_PATH=${STORAGE_PATH:-/data}
FEED_REFRESH_INTERVAL_MINUTES=${FEED_REFRESH_INTERVAL_MINUTES:-30}

# Export for supervisord
export DATABASE_URL REDIS_URL ENVIRONMENT COOKIE_SECURE STORAGE_PATH FEED_REFRESH_INTERVAL_MINUTES

echo "=== Glanced Reader Bundled Setup ==="
echo "Running migrations..."
cd /server
python -m alembic upgrade head

echo "=== Starting all services via supervisord ==="
echo "Services: Backend (port 2076), Frontend (port 2077), Worker"
echo "WebUI will be available at http://localhost:2077"

# Start supervisord (runs as appuser per config)
exec /usr/bin/supervisord -c /etc/supervisord.conf
