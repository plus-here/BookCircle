from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "bio",
            "avatar",
            "avatar_url",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined", "avatar_url"]

    def get_avatar_url(self, obj: User) -> str:
        request = self.context.get("request")
        if obj.avatar and hasattr(obj.avatar, "url"):
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return ""


class RegisterSerializer(serializers.ModelSerializer):
    # ✅ 第1-8行：显式声明字段 + 自定义唯一性错误中文提示
    username = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all(), message="用户名已存在")],
        error_messages={
            "blank": "用户名不能为空",
            "required": "用户名不能为空",
        },
    )

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="邮箱已存在")],
        error_messages={
            "blank": "邮箱不能为空",
            "invalid": "邮箱格式不正确",
        },
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"blank": "密码不能为空", "required": "密码不能为空"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"blank": "确认密码不能为空", "required": "确认密码不能为空"},
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "两次输入的密码不一致"})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
