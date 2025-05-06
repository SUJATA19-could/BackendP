from rest_framework import serializers
from .models import Application
from django.db import models


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'meeting_link']

    def validate_description(self, value):
        if len(value.strip()) < 50:
            raise serializers.ValidationError("Description must be at least 50 characters.")
        return value

    def validate(self, data):
        if data.get("project_type") == "Other" and not data.get("other_project_type"):
            raise serializers.ValidationError({"other_project_type": "Please specify your project type."})
        if data.get("industry") == "Other" and not data.get("other_industry"):
            raise serializers.ValidationError({"other_industry": "Please specify your industry."})
        return data

class MeetingRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        from .models import Application
        if not Application.objects.filter(models.Q(email=value) | models.Q(office_email=value)).exists():
            raise serializers.ValidationError("No application found with this email.")
        return value
