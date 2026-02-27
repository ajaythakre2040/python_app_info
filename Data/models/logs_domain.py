from django.db import models
from django.dispatch import receiver 
from django.db.models.signals import post_save

class domain_logs(models.Model):
    app_data = models.ForeignKey('data.app_data', on_delete = models.CASCADE)
    url = models.URLField(max_length = 500)
    status = models.BooleanField(default=True)
    json_result = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('data.app_data',on_delete=models.SET_NULL,null=True,blank=True,related_name='created_logs')

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('data.app_data',on_delete=models.SET_NULL,null=True,blank=True,related_name='updated_logs')

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey('data.app_data',on_delete=models.SET_NULL,null=True,blank=True,related_name='deleted_logs')

    def save_log(self, status: bool, json_data: dict = None):
        
        self.status = status
        self.url = self.app_data.url
        self.json_result = json_data or {"status": 200 if status else 0, "active": status}
        self.save()

    def __str__(self):
        return f"{self.app_data.title} - {self.status}"