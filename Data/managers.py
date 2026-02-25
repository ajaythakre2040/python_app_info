from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):

    def create_user(self,email_id,name,mobile_number,password=None):
        if not email_id:
            raise ValueError("Email is required")
        email_id = self.normalize_email(email_id)

        user = self.model(email_id=email_id , name= name, mobile_number = mobile_number)
        user .set_password(password)
        user.save(using =self.db)
        return user
    
    def create_superuser(self,email_id , name , mobile_number , password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff')is not True:
            raise ValueError("superuser must have is_staff=True")
        
        if extra_fields.get('is_superuser')is not True:
            raise ValueError("Superuser must have is_superuser=True")
        
        return self.create_user(email_id=email_id, name=name , mobile_number=mobile_number,password=password, **extra_fields)
    