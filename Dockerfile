# Use official Python runtime
FROM python:3.12-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
# Setting a dummy SECRET_KEY for collection if not set in environment
RUN DJANGO_SECRET_KEY=dummy-key-for-build python manage.py collectstatic --noinput

# Expose the port
EXPOSE 8000

# Start server using the dynamic PORT environment variable
CMD ["sh", "-c", "gunicorn tele_crm.wsgi:application --bind 0.0.0.0:${PORT} --workers 3 --timeout 120"]