from rest_framework import serializers

class UnblockUserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=100)  # नया field
    email_id = serializers.EmailField(required=False)
    mobile_number = serializers.CharField(required=False, max_length=10)

    def validate(self, attrs):
        
        if not attrs.get('email_id') and not attrs.get('mobile_number'):
            raise serializers.ValidationError("Either email_id or mobile_number is required.")
        return attrs