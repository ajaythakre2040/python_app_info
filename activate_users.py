#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_project.settings')
django.setup()

from django.contrib.auth.models import User

# Get all inactive users
inactive_users = User.objects.filter(is_active=False)

print(f"Found {inactive_users.count()} inactive users:")
for user in inactive_users:
    print(f"  - {user.username}")

# Activate all inactive users
updated_count = inactive_users.update(is_active=True)
print(f"\n✓ Activated {updated_count} users")

# Verify
active_count = User.objects.filter(is_active=True).count()
print(f"Total active users now: {active_count}")
