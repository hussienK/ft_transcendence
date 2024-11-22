FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Ensure scripts and directories have correct permissions
RUN chmod +x ./wait-for-db.sh
RUN mkdir -p /app/staticfiles && chmod -R 775 /app/staticfiles

# Create a non-root user
RUN useradd -m backenduser && chown -R backenduser:backenduser /app
USER backenduser

EXPOSE 8000

CMD ["sh", "-c", "./wait-for-db.sh db && \
                  python manage.py makemigrations && \
                  python manage.py migrate && \
                  python manage.py create_admin && \
                  python manage.py collectstatic --noinput && \
                  uvicorn ft_transcendance.asgi:application --host 0.0.0.0 --port 8000 --reload"]
