# books/serializers.py
# 行 1
from rest_framework import serializers
from .models import Book, Chapter, Bookshelf, ReadingBookmark


# 行 5
class BookListSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()  # 行 6

    class Meta:  # 行 8
        model = Book
        fields = ["id", "title", "author", "cover_url", "is_published"]  # 行 10

    def get_cover_url(self, obj):  # 行 12
        request = self.context.get("request")
        if obj.cover and hasattr(obj.cover, "url"):
            return request.build_absolute_uri(obj.cover.url) if request else obj.cover.url
        return ""


# 行 19
class BookDetailSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()  # 行 20
    chapters_count = serializers.IntegerField(source="chapters.count", read_only=True)  # 行 21

    class Meta:  # 行 23
        model = Book
        fields = [
            "id", "title", "author", "description", "cover_url", "is_published", "chapters_count", "created_at"
        ]  # 行 28

    def get_cover_url(self, obj):  # 行 30
        request = self.context.get("request")
        if obj.cover and hasattr(obj.cover, "url"):
            return request.build_absolute_uri(obj.cover.url) if request else obj.cover.url
        return ""


# 行 37
class ChapterListSerializer(serializers.ModelSerializer):
    class Meta:  # 行 38
        model = Chapter
        fields = ["id", "book", "order", "title"]  # 行 40


# 行 43
class ChapterDetailSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:  # 行 44
        model = Chapter
        fields = ["id", "book", "book_title", "order", "title", "content"]  # 行 46


# 行 49
class BookshelfSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True, required=True)

    last_read_chapter_info = serializers.SerializerMethodField()

    class Meta:
        model = Bookshelf
        fields = [
            "id",
            "book",
            "book_id",
            "added_at",
            "last_read_chapter",
            "last_read_chapter_info",
            "last_read_at",
        ]
        read_only_fields = [
            "id",
            "added_at",
            "last_read_chapter",
            "last_read_chapter_info",
            "last_read_at",
            "book",
        ]

    def get_last_read_chapter_info(self, obj):
        if obj.last_read_chapter_id:
            c = obj.last_read_chapter
            return {"id": c.id, "order": c.order, "title": c.title}
        return None


class ReadingBookmarkSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    chapter_title = serializers.CharField(source="chapter.title", read_only=True)
    chapter_order = serializers.IntegerField(source="chapter.order", read_only=True)

    class Meta:
        model = ReadingBookmark
        fields = [
            "id",
            "book",
            "book_title",
            "chapter",
            "chapter_title",
            "chapter_order",
            "note",
            "created_at",
        ]
        read_only_fields = ["id", "book", "book_title", "chapter_title", "chapter_order", "created_at"]
