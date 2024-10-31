# FT_TRANSCENDENCE NOTES

## The Constraints

### Docker

- since I can't use docker locally it's been replaced with a venv
- when on a good PC use the following to change
- to check built services `docker-compose ps`
- to run and enter the docker container. in a new shell `docker-compose exec web bash`

### Database

- since I can't use docker nor PostgreSQL development will be done locally on sqllite and will migrate later
- Find the database section and replace it with

``` bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ft_transcendence',
        'USER': 'postgres',
        'PASSWORD': 'HK@12345@42Student',
        'HOST': 'db',
        'PORT': '5432',
    }
}
```

- if data migration is needed then
- dump sqllite data `python manage.py dumpdata > data.json`
- switch to postgre (update settings, restart server) `python manage.py loaddate data.json`

## Dev workflow

- Since the container doesn't have access to the local codebase via bind-mount, you'll need to rebuild the Docker image whenever you make changes to the code.
- `docker-compose build`
- `docker-compose up -d`
