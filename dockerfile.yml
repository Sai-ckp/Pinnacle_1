# Base image
FROM python:3.9-slim

# Install system dependencies for WeasyPrint
# Base image
FROM python:3.9-slim

# Install system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libpango1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libjpeg-dev \
    libxml2 \
    libxslt1.1 \
    libgobject-2.0-0 \
    fonts-liberation \
    fonts-dejavu-core \
    shared-mime-info  # Helps detect file types (needed for PDF)
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy code
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Ensure WeasyPrint's dependencies are resolvable
RUN python -c "from weasyprint import HTML"

# Optional: Collect static files
RUN python manage.py collectstatic --noinput || echo "No static files to collect"

# Set working directory
WORKDIR /app

# Copy code
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Ensure WeasyPrint's dependencies are resolvable
RUN python -c "from weasyprint import HTML"

# Optional: Collect static files
RUN python manage.py collectstatic --noinput || echo "No static files to collect"

# Expose port
EXPOSE 8000

# Start app
CMD ["gunicorn", "student_alerts_app.wsgi:application", "--bind", "0.0.0.0:8000"]
