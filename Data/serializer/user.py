import re
from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from ..models import User
from ..models.password_history import Password_History
from ..utils.password import validate_custom_password, is_password_reused
from ..utils.email import check_email

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required = False)

    class Meta:
        model = User 
        fields = "__all__"
        read_only_fields = ['created_at','updated_at','deleted_at',]

    def validate_email_id(self, value):

        if not check_email(value):
            raise serializers.ValidationError(
            "Invalid email. Email must start with a lowercase letter and follow proper format."
        )

        return value
    
    def validate_password(self,value):
        value = validate_custom_password(value)

        user = self.instance
        if user and is_password_reused(user, value):
            raise serializers.ValidationError("password was used recently")
        return value
    
    def validate_mobile_number(self, value):
        if not re.fullmatch(r'^\d{10}$', value):
            raise serializers.ValidationError("Mobile number must contain exactly 10 digits and only numbers are allowed.")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data["password"] = make_password(password)
        user = super().create(validated_data)
        Password_History.objects.create(user=user, password=user.password)
        return user
    
    def update(self, instance, validated_data):
        validated_data.pop("password", None)   # password update block
        return super().update(instance, validated_data)

