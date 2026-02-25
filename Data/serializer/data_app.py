from rest_framework import serializers
from ..models import App_Data
from ..utils.sanitize import no_html_validator

SANITIZE_FIELDS = ['title','description','url_test']

class AppDataSerializer(serializers.ModelSerializer):
    title = serializers.CharField(validators=[no_html_validator])
    description = serializers.CharField(required = False, allow_blank = True,validators=[no_html_validator])
    url_test = serializers.CharField(validators=[no_html_validator])

    class Meta:
        model = App_Data
        fields="__all__"
        read_only_fields = ["id","created_at","updated_at","deleted_at"]
    