# ---------------------------- External Imports ----------------------------
# Use official Python 3.11 slim image for smaller footprint
FROM python:3.11-slim

# ---------------------------- Setup ----------------------------
# Set working directory inside container
WORKDIR /app

# Install system dependencies:
# - gcc, libpq-dev: needed to compile psycopg2 (Postgres driver)
# - postgresql-client: provides pg_isready to check DB availability
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------- Copy Dependencies ----------------------------
# Copy Python requirements file first to leverage Docker cache
COPY backend/requirements.txt .

# Install Python dependencies without caching
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------- Copy App Source ----------------------------
# Copy backend source code into container
COPY backend/ .

# ---------------------------- Expose Ports ----------------------------
# Expose FastAPI default port (used only when running backend service)
EXPOSE 8000

# ---------------------------- CMD ----------------------------
# Default command: start Uvicorn server for FastAPI
# NOTE: In docker-compose we override this for Celery and Alembic services
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
