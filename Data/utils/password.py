import re
from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from ..models.password_history import Password_History

def validate_custom_password(password):

    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters long")
    
    if not password[0].isupper():
        raise serializers.ValidationError("Password first letter must be capital")
    
    if not re.search(r"[a-z]", password):
        raise serializers.ValidationError("Password must contain at least one lowercase letter")

    if not re.search(r"\d",password):
        raise serializers.ValidationError("password must contain at least one digit")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise serializers.ValidationError("Password must contain at least one special character")
    return password

def is_password_reused(user, new_password, limit=3):
    last_passwords = Password_History.objects.filter(user=user).order_by('-id')[:limit]

    for history in last_passwords:
        if check_password(new_password, history.password):
            return True  

    return False  