from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Create a superuser from environment variables'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'Nitingouda')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'nitingouda@gmail.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'patil@5156')
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {username} already exists')) 