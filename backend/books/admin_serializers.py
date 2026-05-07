from rest_framework import serializers
from .models import Book, Chapter


class BookAdminSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "description",
            "cover", "cover_url",
            "is_published", "created_at", "updated_at",
        ]

    def get_cover_url(self, obj):
        request = self.context.get("request")
        if obj.cover and hasattr(obj.cover, "url"):
            return request.build_absolute_uri(obj.cover.url) if request else obj.cover.url
        return ""


class ChapterAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ["id", "book", "order", "title", "content", "created_at", "updated_at"]
