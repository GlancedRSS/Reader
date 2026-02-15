#!/bin/sh
set -e

ROLE=${ROLE:-server}

case "$ROLE" in
    frontend)
        echo "Starting Glanced Reader Frontend..."
        cd /app
        exec node server.js
        ;;

    server|worker)
        echo "Starting Glanced Reader Backend ($ROLE)..."
        cd /server

        echo "Waiting for database..."
        max_tries=5
        counter=0
        until pg_isready -h db -U postgres 2>&1; do
            counter=$((counter + 1))
            if [ $counter -ge $max_tries ]; then
                echo "Database unavailable after $max_tries attempts. Exiting."
                exit 1
            fi
            echo "Database unavailable, retrying in 15s... ($counter/$max_tries)"
            sleep 15
        done
        echo "Database is ready."

        if [ "$ROLE" = "server" ]; then
            echo "Running migrations..."
            python -m alembic upgrade head
        fi

        echo "Starting $ROLE..."
        if [ "$ROLE" = "worker" ]; then
            exec python -m arq backend.workers.settings.WorkerSettings
        else
            exec python -m uvicorn backend.main:app --host 0.0.0.0 --port 2076
        fi
        ;;

    *)
        echo "Invalid ROLE: $ROLE (must be 'frontend', 'server', or 'worker')"
        exit 1
        ;;
esac
