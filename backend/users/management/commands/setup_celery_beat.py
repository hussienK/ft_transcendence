from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from celery import current_app

class Command(BaseCommand):
    help = "Setup periodic tasks for Celery Beat"

    def handle(self, *args, **kwargs):
        # Get all registered tasks from the current Celery app
        registered_tasks = current_app.tasks.keys()

        self.stdout.write(self.style.WARNING("Cleaning up unregistered periodic tasks..."))
        unregistered_tasks = PeriodicTask.objects.exclude(task__in=registered_tasks)
        count = unregistered_tasks.count()
        unregistered_tasks.delete()
        self.stdout.write(self.style.SUCCESS(f"Removed {count} unregistered periodic tasks."))

        self.stdout.write(self.style.WARNING("Setting up periodic tasks..."))

        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        # Create or update the "Mark users offline" task
        task, created = PeriodicTask.objects.get_or_create(
            interval=schedule,
            name="Mark users offline after inactivity",
            defaults={"task": "users.tasks.mark_users_offline"},
        )
        if not created:
            task.task = "users.tasks.mark_users_offline" 
            task.save()

        self.stdout.write(self.style.SUCCESS("Periodic task registered or updated."))
