import hashlib
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import Login_logout_history

class LoginTokenAuthentication(BaseAuthentication):
    """
    Custom authentication using JWT token + session history.
    Only active users are allowed.
    """

    def authenticate(self, request):
        auth_header = get_authorization_header(request).split()
        if not auth_header or auth_header[0].lower() != b'bearer':
            raise AuthenticationFailed("Authorization header missing or invalid")

        if len(auth_header) != 2:
            raise AuthenticationFailed("Invalid token header. Correct format: Bearer <token>")

        raw_token = auth_header[1].decode()

        # Validate JWT
        jwt_auth = JWTAuthentication()
        try:
            validated_token = jwt_auth.get_validated_token(raw_token)
            user = jwt_auth.get_user(validated_token)
        except Exception as e:
            raise AuthenticationFailed(f"Invalid or expired token: {str(e)}")

        # Ensure user is active
        if not user.is_active:
            raise AuthenticationFailed("User account is inactive. Please contact admin.")

        # Check session in Login_logout_history
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        session = Login_logout_history.objects.filter(
            user=user,
            token_hash=token_hash,
            logout_time__isnull=True
        ).first()

        if not session:
            raise AuthenticationFailed("Session expired or logged out")

        if session.expires_at and session.expires_at < timezone.now():
            raise AuthenticationFailed("Session expired")

        # Optional: User-Agent binding
        request_ua = request.META.get('HTTP_USER_AGENT', '')
        if session.user_agent and session.user_agent != request_ua:
            raise AuthenticationFailed("Token cannot be used in a different browser/device")

        # Optional: IP binding
        request_ip = request.META.get('REMOTE_ADDR')
        if session.ip_address and session.ip_address != request_ip:
            raise AuthenticationFailed("Token cannot be used from a different IP")

        return (user, validated_token)