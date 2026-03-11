import hashlib
from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from data.models.login_logout_history import Login_logout_history
from django.conf import settings  

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def token_generate(user, request, log_history=True):
    # 1. JWT Tokens Generate karein
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # 2. Settings.py se Expiry Time nikaalein (Dynamic Logic)
    jwt_config = getattr(settings, "SIMPLE_JWT", {})
    access_token_lifetime = jwt_config.get("ACCESS_TOKEN_LIFETIME")

    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    expires_at = timezone.now() + access_token_lifetime

    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    ip_address = get_client_ip(request)
    token_hash = hashlib.sha256(access_token.encode()).hexdigest()

    # optional history logging
    if log_history:
        Login_logout_history.objects.create(
            user=user,
            login_time=timezone.now(),
            token_hash=token_hash,
            session_key=session_key,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True,
        )

    return {"access": access_token, "refresh": refresh_token}
