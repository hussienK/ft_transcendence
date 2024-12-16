# Use slim Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install OS-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (to leverage caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN useradd -m backenduser

# Copy the application code and set ownership
COPY . /app
RUN chown -R backenduser:backenduser /app

# Ensure necessary directories exist and set correct ownership/permissions
RUN mkdir -p /app/media/avatars /app/staticfiles && \
    chown -R backenduser:backenduser /app/media /app/staticfiles && \
    chmod -R 755 /app/media /app/staticfiles && \
    chmod +x ./wait-for-db.sh

# Switch to the non-root user
USER backenduser

# Expose the application port
EXPOSE 8000

# Define the default command
CMD ["sh", "-c", "./wait-for-db.sh db && \
                  python manage.py makemigrations && \
                  python manage.py migrate && \
                  python manage.py create_admin && \
                  python manage.py collectstatic --noinput && \
                  uvicorn ft_transcendance.asgi:application --host 0.0.0.0 --port 8000 --reload"]
