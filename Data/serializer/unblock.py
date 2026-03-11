from rest_framework import serializers
from ..models import UnblockUser

class UnblockUserSerializer(serializers.ModelSerializer):
    email_id = serializers.EmailField(required=True)
    mobile_number = serializers.CharField(required=True, max_length=10)

    class Meta:
        model = UnblockUser
        fields = ['email_id', 'mobile_number'] 