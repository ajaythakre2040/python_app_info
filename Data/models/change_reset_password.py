from django.conf import settings
from django.db import models

class Password_Action_Log(models.Model):

    ACTION_CHOICES = (
        ('change', 'Password Change'),
        ('reset', 'Password Reset'),)

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='password_actions')

    action_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='performed_password_actions')

    action_type = models.CharField(max_length=10,choices=ACTION_CHOICES)

    action_count = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "password_action_log"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action_type} - {self.action_count}"