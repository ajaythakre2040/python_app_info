from django.db import models

class app_data(models.Model):
    user = models.ForeignKey('data.User', on_delete=models.CASCADE, related_name='app_data')
    
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    description = models.TextField(max_length=255, blank=True, null=True)
    status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('data.User',on_delete=models.SET_NULL, null=True, blank= True, related_name='data_created')

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('data.User',on_delete=models.SET_NULL,null=True, blank=True, related_name='data_updated')

    deleted_at = models.DateTimeField(null=True,blank=True)
    deleted_by = models.ForeignKey('data.User',on_delete=models.SET_NULL, null=True, blank=True, related_name='data_deleted')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  
        
        user_records = app_data.objects.filter(
            user_id=self.user_id,
            deleted_at__isnull=True
        ).order_by('-created_at')

        if user_records.count() > 5:
            to_delete = user_records[5:]  
            for record in to_delete:
                record.delete()  