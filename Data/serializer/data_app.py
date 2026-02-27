from rest_framework import serializers
from ..models import app_data
from ..utils.sanitize import no_html_validator

SANITIZE_FIELDS = ['title','description','url']

class AppDataSerializer(serializers.ModelSerializer):
    title = serializers.CharField(validators=[no_html_validator])
    description = serializers.CharField(required = False, allow_blank = True,validators=[no_html_validator])
    url = serializers.CharField(validators=[no_html_validator])

    class Meta:
        model = app_data
        fields="__all__"
        read_only_fields = ["id","created_at","updated_at","deleted_at","user",]
    