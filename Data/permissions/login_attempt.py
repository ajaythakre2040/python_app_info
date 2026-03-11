from rest_framework.exceptions import ValidationError

MAX_LOGIN_ATTEMPTS = 3

def check_login_attempts(user):
    if user.login_attempts >= MAX_LOGIN_ATTEMPTS or not user.is_active:
        raise ValidationError("Too many login attempts. User is blocked. Please contact admin.")

def register_failed_attempt(user):
    if not user.is_active:
        return

    user.login_attempts += 1

    if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
        user.is_active = False

    user.save()

def reset_login_attempts(user):
    user.login_attempts = 0
    user.is_active = True 
    user.save()