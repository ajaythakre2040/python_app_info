#!/usr/bin/env python
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_project.settings')
django.setup()

from Data.models.user import User

try:
    # Get all inactive users
    inactive_users = User.objects.filter(is_active=False)
    
    print(f"Found {inactive_users.count()} inactive users:")
    for user in inactive_users:
        print(f"  - {user.username} (id: {user.id})")
    
    # Activate all inactive users
    updated_count = inactive_users.update(is_active=True)
    print(f"\n✓ Activated {updated_count} users")
    
    # Verify
    active_count = User.objects.filter(is_active=True).count()
    inactive_count = User.objects.filter(is_active=False).count()
    print(f"\nStatus:")
    print(f"  Active users: {active_count}")
    print(f"  Inactive users: {inactive_count}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
