#!/bin/bash

# Exit on error
set -e

# Function to extract host from DATABASE_URL
get_db_host() {
    if [ -n "$DATABASE_URL" ]; then
        # Extract host from DATABASE_URL (format: postgresql://user:pass@host:port/db)
        echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+).*|\1|'
    elif [ -n "$DB_HOST" ]; then
        echo "$DB_HOST"
    else
        echo ""
    fi
}

# Function to extract port from DATABASE_URL
get_db_port() {
    if [ -n "$DATABASE_URL" ]; then
        # Extract port from DATABASE_URL, default to 5432 if not specified
        PORT=$(echo "$DATABASE_URL" | sed -E 's|.*:([0-9]+)/.*|\1|')
        if [[ "$PORT" =~ ^[0-9]+$ ]]; then
            echo "$PORT"
        else
            echo "5432"
        fi
    else
        echo "${DB_PORT:-5432}"
    fi
}

# Function to extract user from DATABASE_URL
get_db_user() {
    if [ -n "$DATABASE_URL" ]; then
        # Extract user from DATABASE_URL
        echo "$DATABASE_URL" | sed -E 's|.*://([^:]+):.*|\1|'
    else
        echo "${DB_USER:-postgres}"
    fi
}

DB_HOST=$(get_db_host)
DB_PORT=$(get_db_port)
DB_USER=$(get_db_user)

# Wait for PostgreSQL only if we have a host to check
if [ -n "$DB_HOST" ]; then
    echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT (max 30 seconds)..."

    TIMEOUT=30
    ELAPSED=0

    while [ $ELAPSED -lt $TIMEOUT ]; do
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
            echo "PostgreSQL is ready!"
            break
        fi
        sleep 1
        ELAPSED=$((ELAPSED + 1))
    done

    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "Warning: PostgreSQL readiness check timed out after ${TIMEOUT}s. Proceeding anyway..."
    fi
else
    echo "No database host configured, skipping PostgreSQL readiness check..."
fi

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn on port $PORT..."
exec gunicorn shop.wsgi:application --bind 0.0.0.0:$PORT --workers 2
