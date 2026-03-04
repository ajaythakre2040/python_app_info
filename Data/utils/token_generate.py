import hashlib
from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from data.models.login_logout_history import Login_logout_history
from django.conf import settings  # Settings import karein

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def token_generate(user, request):
    # 1. JWT Tokens Generate karein
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # 2. Settings.py se Expiry Time nikaalein (Dynamic Logic)
    # Aapne settings mein 10 hours set kiya hai, ye wahi se uthayega
    jwt_config = getattr(settings, "SIMPLE_JWT", {})
    access_token_lifetime = jwt_config.get("ACCESS_TOKEN_LIFETIME")

    # Expiry calculate karein
    expires_at = timezone.now() + access_token_lifetime

    # 3. Session key handle karein
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # 4. IP Address aur Token Hash
    ip_address = get_client_ip(request)
    token_hash = hashlib.sha256(access_token.encode()).hexdigest()

    # 5. History Table mein entry karein
    Login_logout_history.objects.create(
        user=user,
        token_hash=token_hash,
        session_key=session_key,
        ip_address=ip_address,
        expires_at=expires_at,  # Ab ye barabar 10 hours baad ki date save karega
        is_active=True,
    )

    return {"access": access_token, "refresh": refresh_token}
