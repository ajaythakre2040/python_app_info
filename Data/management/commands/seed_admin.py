from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from data.models.user import User  
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Command(BaseCommand):
    help = 'Create a super admin user using .env file and show details in terminal'

    def handle(self, *args, **kwargs):
        try:
            # Read credentials from .env
            admin_email = os.getenv("ADMIN_EMAIL")
            admin_password = os.getenv("ADMIN_PASSWORD")
            admin_name = os.getenv("ADMIN_NAME")
            admin_mobile = os.getenv("ADMIN_MOBILE")

            if not all([admin_email, admin_password, admin_name, admin_mobile]):
                self.stderr.write("✗ Error: Some environment variables are missing!")
                return

            user, created = User.objects.get_or_create(
                email_id=admin_email,
                defaults={
                    "name": admin_name,
                    "mobile_number": admin_mobile,
                    "password": make_password(admin_password),
                    "is_active": True,
                    "is_staff": True,
                    "is_superuser": True
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS('Admin created successfully!'))
            else:
                self.stdout.write(self.style.SUCCESS('✓ Admin already exists'))

            self.stdout.write(f"Email: {user.email_id}")
            self.stdout.write(f"Name: {user.name}")
            self.stdout.write(f"Mobile: {user.mobile_number}")

        except Exception as e:
            self.stderr.write(f"✗ Error: {e}")