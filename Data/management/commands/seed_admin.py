from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from data.models.user import User  

class Command(BaseCommand):
    help = 'Create a super admin user (without .env) and show details in terminal'

    def handle(self, *args, **kwargs):
        try:
  
            admin_email = "admin@example.com"
            admin_password = "Admin@123"  
            admin_name = "Super Admin"
            admin_mobile = "9999999999"

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