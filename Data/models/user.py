from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models 
from ..managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    name= models.CharField(max_length=100)
    mobile_number =models.CharField(max_length=15,unique=True,null=True,blank=True)
    email_id = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True,related_name='created_users')

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True,related_name='updated_users')

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True,related_name='deleted_users')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email_id'
    REQUIRED_FIELDS = ['name','mobile_number']

    def __str__(self):
        return self.email_id