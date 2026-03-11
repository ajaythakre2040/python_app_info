from django.db import models
from django.conf import settings

class UnblockUser(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="unblock_user")

    name = models.CharField(max_length=150)
    email_id = models.EmailField(null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="unblock_created_by")

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="unblock_updated_by")

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="unblock_deleted_by")

    class Meta:
        db_table = "user_unblock_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name