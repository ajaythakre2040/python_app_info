from django.db import models

class App_Data(models.Model):
    
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    description = models.TextField(max_length=255, blank=True, null=True)
    status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('Data.User',on_delete=models.SET_NULL, null=True, blank= True, related_name='data_created')

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('Data.User',on_delete=models.SET_NULL,null=True, blank=True, related_name='data_updated')

    deleted_at = models.DateTimeField(null=True,blank=True)
    deleted_by = models.ForeignKey('Data.User',on_delete=models.SET_NULL, null=True, blank=True, related_name='data_deleted')

    def __str__(self):
        return self.title
    