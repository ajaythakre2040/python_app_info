MAX_LOGIN_ATTEMPTS = 3

def check_login_attempts(user):
    if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
        raise Exception("Too many login attempts. User is blocked.")


def register_failed_attempt(user):
    if not user.is_active:
        return

    user.login_attempts += 1

    if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
        user.is_active = False

    user.save(update_fields=["login_attempts", "is_active"])


def reset_login_attempts(user):
    user.login_attempts = 0
    user.save(update_fields=["login_attempts"])