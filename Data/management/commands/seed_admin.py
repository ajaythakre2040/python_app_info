from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from decouple import config
from Data.models.user import User

class Command(BaseCommand):
    help = 'Create a super admin user from .env'

    def handle(self, *args, **kwargs):
        try:
            admin_email = config("ADMIN_EMAIL")
            admin_password = config("ADMIN_PASSWORD")
            admin_name = config("ADMIN_NAME", default="Super Admin")
            admin_mobile = config("ADMIN_MOBILE", default="9999999999")

            if User.objects.filter(email_id=admin_email).exists():
                self.stdout.write(self.style.SUCCESS('✓ Admin already exists'))
            else:
                User.objects.create(
                    email_id=admin_email,
                    name=admin_name,
                    mobile_number=admin_mobile,
                    password=make_password(admin_password),
                    is_active=True,
                    is_staff=True,
                    is_superuser=True
                )
                self.stdout.write(self.style.SUCCESS('Admin created successfully'))

        except Exception as e:
            self.stderr.write(f"✗ Error: {e}")