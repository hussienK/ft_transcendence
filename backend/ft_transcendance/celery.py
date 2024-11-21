from __future__ import absolute_import, unicode_literals
import os
import logging
from celery import Celery
from django.conf import settings

# Set default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ft_transcendance.settings')

app = Celery('ft_transcendance')

# Use 'CELERY_' prefix for all Celery-related settings in Django.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

# Update configuration (optional)
app.conf.update(
    broker_connection_retry_on_startup=True,
)

# Discover tasks from all installed apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Debugging task for testing
logger = logging.getLogger(__name__)

@app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')
