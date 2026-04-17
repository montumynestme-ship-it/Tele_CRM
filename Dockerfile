# Use official Python runtime as a parent image
FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files at build time
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run migrations then start gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn tele_crm.wsgi:application --bind 0.0.0.0:8000 --workers 4"]
