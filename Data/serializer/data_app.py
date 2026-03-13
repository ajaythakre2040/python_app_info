from psycopg2 import IntegrityError
from rest_framework import serializers
from ..models import app_data
from ..utils.sanitize import no_html_validator

SANITIZE_FIELDS = ['title','description','url']

class AppDataSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255, validators=[no_html_validator])
    description = serializers.CharField(max_length=255, required = False, allow_blank = True,validators=[no_html_validator])
    url = serializers.CharField(max_length=255, validators=[no_html_validator])

    class Meta:
        model = app_data
        fields="__all__"
        read_only_fields = ["id","created_at","updated_at","deleted_at","user",]


    def validate_url(self, value):
        qs = app_data.objects.filter(url=value, deleted_at__isnull=True)

        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            raise serializers.ValidationError(
                "A record with this URL already exists."
            )
        return value
    
    # create method
    def create(self, validated_data):
        try:
            return app_data.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                "url": "This URL already exists."
            })

    # update method
    def update(self, instance, validated_data):
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()
            return instance

        except IntegrityError:
            raise serializers.ValidationError({
                "url": "This URL already exists."
            })