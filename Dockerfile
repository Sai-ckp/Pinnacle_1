# Stage 1: Build dependencies and static assets
FROM python:3.9-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy requirements first to install dependencies early (use Docker cache)
COPY requirements.txt ./

# Install WeasyPrint system dependencies and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libffi-dev shared-mime-info \
      libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
      libgdk-pixbuf2.0-0 libgobject-2.0-0 \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy all source code
COPY . .

# Ensure WeasyPrint loads properly
RUN python -c "from weasyprint import HTML" && \
    python manage.py collectstatic --noinput

# Stage 2: Final image with runtime dependencies
FROM python:3.9-slim AS production

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 🔧 Install WeasyPrint runtime dependencies (again — required!)
RUN apt-get update && apt-get install -y --no-install-recommends \
      libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
      libgdk-pixbuf2.0-0 libgobject-2.0-0 shared-mime-info \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy project from builder
COPY --from=builder /app /app

# Set correct permissions
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000
CMD ["gunicorn", "student_alerts_app.wsgi:application", "--bind", "0.0.0.0:8000"]
