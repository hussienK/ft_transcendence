FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN useradd -m backenduser && chown -R backenduser:backenduser /app
USER backenduser

#use port 8000
EXPOSE 8000

#migrate, create_admin user through a task, collects static data, starts the app with uvicorn
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py create_admin && python manage.py collectstatic --noinput && uvicorn ft_transcendance.asgi:application --host 0.0.0.0 --port 8000 --reload"]
