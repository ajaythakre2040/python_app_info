import hashlib
from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from data.models.login_logout_history import Login_logout_history

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def token_generate(user, request):
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # Session key
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # Client IP
    ip_address = get_client_ip(request)

    expires_at = timezone.now() + timedelta(hours=1)

    # Save hash of raw access token (do NOT modify JWT)
    token_hash = hashlib.sha256(access_token.encode()).hexdigest()

    Login_logout_history.objects.create(
        user=user,
        token_hash=token_hash,
        session_key=session_key,
        ip_address=ip_address,
        expires_at=expires_at,
        is_active=True
    )

    return {"access": access_token, "refresh": refresh_token}