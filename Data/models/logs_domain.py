from django.db import models

class domain_logs(models.Model):
    app_data = models.ForeignKey('data.app_data', on_delete = models.CASCADE)
    url = models.URLField(max_length = 255)
    status = models.BooleanField(default=True)
    json_result = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('data.app_data',on_delete=models.SET_NULL,null=True,blank=True,related_name='created_logs')

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('data.app_data',on_delete=models.SET_NULL,null=True,blank=True,related_name='updated_logs')

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey('data.app_data',on_delete=models.SET_NULL,null=True,blank=True,related_name='deleted_logs')

    def save_log(self, status: bool, http_status: int = None):

        self.status = status
        self.url = self.app_data.url
        self.json_result = {
        "active": status,
        "http_status": http_status
    }
        self.save()

    def __str__(self):
        return f"{self.app_data.title} - {self.status}"