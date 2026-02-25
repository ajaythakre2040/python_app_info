import re
from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from ..models import User
from ..models.password_history import Password_History
from ..utils.password import validate_custom_password, is_password_reused

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required = False)

    class Meta:
        model = User 
        fields = "__all__"
        read_only_fields = ['is_active','created_at','updated_at','deleted_at',]

    def validate_password(self,value):
        value = validate_custom_password(value)

        user = self.instance
        if user and is_password_reused(user, value):
            raise serializers.ValidationError("password was used recently")
        return value
    
    def validate_mobile_number(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("mobile number must be exactly 10")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data["password"] = make_password(password)
        user = super().create(validated_data)
        Password_History.objects.create(user=user, password=user.password)
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop("password",None)
        if password:
            validated_data["password"]=make_password(password)
            Password_History.objects.create(user=instance, password= validated_data["password"])
        return super().update(instance, validated_data)

