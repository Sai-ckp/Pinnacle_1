# Stage 1: Builder stage installs dependencies and builds assets
FROM python:3.9-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy dependency file first to improve cache utilization
COPY requirements.txt ./

# Install runtime and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
      libgdk-pixbuf2.0-0 libffi-dev shared-mime-info \
      libgobject-2.0-0 build-essential \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files and collect static assets
COPY . .

RUN python -c "from weasyprint import HTML" && \
    python manage.py collectstatic --noinput

# Stage 2: Final runtime image
FROM python:3.9-slim AS production

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create and switch to a non-root user
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

# Copy only necessary files from builder stage
COPY --from=builder /app /app

# Set ownership and drop privileges
RUN chown -R appuser:appgroup /app
USER appuser

# Expose app port and start command
EXPOSE 8000
CMD ["gunicorn", "student_alerts_app.wsgi:application", "--bind", "0.0.0.0:8000"]
