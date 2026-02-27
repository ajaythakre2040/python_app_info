from rest_framework import serializers
from ..models import User

class DomainSerializer(serializers.ModelSerializer):
    
    created_by_name = serializers.CharField(source='created_by.name', default=None)
    updated_by_name = serializers.CharField(source='updated_by.name', default=None)
    deleted_by_name = serializers.CharField(source='deleted_by.name', default=None)

    class Meta:
        model = User
        fields = ['id',
                  'name',
                  'email_id',
                  'mobile_number',
                  'is_active',
                  'created_at',
                  'created_by_name',
                  'updated_at',
                  'updated_by_name',
                  'deleted_at',
                  'deleted_by_name']
