from django.conf import settings
from django.db import models

class Password_History(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_histories')
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "password_history"
        ordering = ['-created_at']

    def __str__(self):
        return f"PasswordHistory - {self.user.email_id} at= {self.created_at}"
