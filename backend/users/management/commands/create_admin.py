from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
from dotenv import load_dotenv

load_dotenv()
class Command(BaseCommand):
    help = 'Create a default admin user if not already created'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        admin_email = os.getenv('ADMIN_EMAIL')
        admin_display_name = os.getenv('ADMIN_DISPLAY_NAME')
        admin_username = os.getenv('ADMIN_USERNAME')
        admin_password = os.getenv('ADMIN_PASSWORD')

        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                display_name=admin_display_name,
                password=admin_password
            )
            self.stdout.write(self.style.SUCCESS('Admin user created.'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists.'))
