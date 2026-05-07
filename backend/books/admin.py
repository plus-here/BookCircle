# books/admin.py
# 行 1
from django.contrib import admin
from .models import Book, Chapter, Bookshelf


# 行 5
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "is_published", "created_at")  # 行 7
    search_fields = ("title", "author")  # 行 8
    list_filter = ("is_published",)  # 行 9


# 行 12
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "order", "title", "updated_at")  # 行 14
    search_fields = ("title", "book__title")  # 行 15
    list_filter = ("book",)  # 行 16
    ordering = ("book", "order")  # 行 17


# 行 20
@admin.register(Bookshelf)
class BookshelfAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "added_at", "last_read_chapter", "last_read_at")  # 行 22
    search_fields = ("user__username", "book__title")  # 行 23
    list_filter = ("user",)  # 行 24
