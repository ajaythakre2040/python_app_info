from rest_framework import serializers
from ..models import User
from ..utils import validate_custom_password
from ..models.password_history import Password_History
from ..utils.email import check_email
import re

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only =True, required = True)

    class Meta:
        model =User
        fields = "__all__"

    def validate_email_id(self, value):

        if not check_email(value):
            raise serializers.ValidationError(
            "Invalid email. Email must start with a lowercase letter and follow proper format."
        )

        return value
    
    def validate_password(self, value):
            validate_custom_password(value)
            return value

    def validate_mobile_number(self, value):
        if not re.fullmatch(r'^\d{10}$', value):
            raise serializers.ValidationError(
                "Mobile number must contain exactly 10 digits and only numbers are allowed."
            )
        return value


    def create(self, validated_data):
        password = validated_data.pop('password')
        print("Validated data:", validated_data)
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        Password_History.objects.create(user=user, password=user.password)
        return user
        
#=======================CHANGEPASSWORD ===========================#        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required = True,write_only =True)
    new_password = serializers.CharField(required = True , write_only = True)

    def validate_new_password(self,value):
        validate_custom_password(value)
        return value

#========================RESET PASSWORD ===========================#
class ResetPasswordSerializer(serializers.Serializer):
    email_id = serializers.EmailField(required = False)
    mobile_number = serializers.CharField(required = False, max_length = 15)
    new_password = serializers.CharField(write_only = True, required = True)

    def validate_new_password(self, value):
        return validate_custom_password(value)