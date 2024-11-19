from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a default admin user if not already created'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        admin_email = 'admin1@example.com'
        admin_display_name = 'admin1'
        admin_username = 'admin1'
        admin_password = 'adminpassword'  # Replace with a secure password or read from env

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
