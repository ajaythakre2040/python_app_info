from django.db import models
from django.conf import settings

class Login_logout_history(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    token_hash = models.CharField(max_length=255, unique=True)
    session_key =models.CharField(max_length=255, null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    login_time =models.DateTimeField(auto_now_add=True) 
    logout_time = models.DateTimeField(null=True, blank=True)

    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user}-{self.login_time}"
    