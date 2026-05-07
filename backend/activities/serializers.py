from rest_framework import serializers
from .models import Activity, ActivitySignup, Club


class ActivitySerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    target_clubs = serializers.SerializerMethodField()
    target_club_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="要分发的社团ID列表",
    )

    class Meta:
        model = Activity
        fields = [
            "id", "title", "description", "location",
            "start_time", "end_time", "signup_deadline",
            "status", "created_by", "created_by_username",
            "target_clubs", "target_club_ids",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_username", "target_clubs", "created_at"]

    def get_target_clubs(self, obj):
        return [{"id": c.id, "name": c.name} for c in obj.targets.all()]


class ActivitySignupSerializer(serializers.ModelSerializer):
    activity_title = serializers.CharField(source="activity.title", read_only=True)
    club_name = serializers.CharField(source="club.name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ActivitySignup
        fields = ["id", "activity", "activity_title", "club", "club_name", "user", "username", "status", "created_at"]
        read_only_fields = ["id", "created_at", "username", "club_name", "activity_title"]

from rest_framework import serializers
from .models import Activity, ActivitySignup

class ActivitySerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    signed_count = serializers.SerializerMethodField()
    remaining_slots = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    my_signup_status = serializers.SerializerMethodField()

    target_clubs = serializers.SerializerMethodField()
    target_club_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="要分发的社团ID列表",
    )

    class Meta:
        model = Activity
        fields = [
            "id", "title", "description", "location",
            "start_time", "end_time", "signup_deadline",
            "capacity", "signed_count", "remaining_slots", "is_full",
            "my_signup_status", "status", "created_by", "created_by_username",
            "target_clubs", "target_club_ids",
            "created_at",
        ]
        read_only_fields = [
            "id", "created_by", "created_by_username", "target_clubs",
            "signed_count", "remaining_slots", "is_full", "my_signup_status", "created_at",
        ]

    def get_target_clubs(self, obj):
        return [{"id": c.id, "name": c.name} for c in obj.targets.all()]

    def get_signed_count(self, obj):
        return obj.signups.filter(status="signed").count()

    def get_remaining_slots(self, obj):
        if not obj.capacity:
            return None
        return max(obj.capacity - self.get_signed_count(obj), 0)

    def get_is_full(self, obj):
        return bool(obj.capacity and self.get_signed_count(obj) >= obj.capacity)

    def get_my_signup_status(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return None
        signup = obj.signups.filter(user=request.user).first()
        return signup.status if signup else None

    # ✅ 关键：创建时，把 target_club_ids 从 validated_data 里拿掉再创建 Activity
    def create(self, validated_data):
        ids = validated_data.pop("target_club_ids", [])
        activity = Activity.objects.create(**validated_data)
        # ✅ 设置分发社团（ManyToMany）
        if ids is not None:
            activity.targets.set(ids)
        return activity

    # ✅ 关键：更新时同样处理 target_club_ids
    def update(self, instance, validated_data):
        ids = validated_data.pop("target_club_ids", None)

        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()

        # 传了 target_club_ids 就更新（哪怕是 [] 也要能清空）
        if ids is not None:
            instance.targets.set(ids)

        return instance
