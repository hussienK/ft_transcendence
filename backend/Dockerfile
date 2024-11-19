FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Ensure non-root user can access /app
RUN useradd -m backenduser && chown -R backenduser:backenduser /app
USER backenduser

EXPOSE 8000
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && uvicorn ft_transcendance.asgi:application --host 0.0.0.0 --port 8000 --reload"]
