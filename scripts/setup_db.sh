#!/usr/bin/env bash

# Exit on error
set -e

echo "🚀 Starting Database Setup..."

# Load environment variables from .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

DB_USER=${POSTGRES_USER:-fastapi}
DB_NAME=${POSTGRES_DB:-fastapi}
DB_PASS=${POSTGRES_PASSWORD:-fastapi}

echo "🛠️ Creating User and Database for: $DB_NAME"

# Execute PostgreSQL commands as the postgres system user
# This might prompt for your sudo password
sudo -u postgres psql <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASS' SUPERUSER;
    END IF;
END
\$\$;

SELECT 'Database check...';
IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME') THEN
    CREATE DATABASE $DB_NAME OWNER $DB_USER;
END IF;
EOF

# Special case for DB creation since it can't be run inside a DO block easily
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER"

echo "✅ Database and User are ready."

# Run migrations to create tables
echo "🏗️ Running migrations..."
source .venv/bin/activate
alembic upgrade head

echo "✨ Setup complete! Everything is ready to go."
