from rest_framework import serializers
from .models import User


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active", "is_staff", "is_superuser", "created_at", "last_login"]
        read_only_fields = ["id", "username", "is_superuser", "created_at", "last_login"]
