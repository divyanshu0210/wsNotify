from django.contrib.auth import get_user_model
import os

def run():
    User = get_user_model()
    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "nsadmin")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL", "nsadmin@example.com")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "nsadmin")

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        
