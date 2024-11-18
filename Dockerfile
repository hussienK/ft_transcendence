FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE ft_transcendance.settings

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/
COPY backend/init.sql /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/backend/

RUN chmod -R 755 /app

EXPOSE 8000

WORKDIR /app/backend

CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
