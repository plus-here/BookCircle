# books/models.py
# 行 1
from django.conf import settings
from django.db import models


# 行 6
class Book(models.Model):
    title = models.CharField(max_length=200)  # 行 7
    author = models.CharField(max_length=100, blank=True, default="")  # 行 8
    description = models.TextField(blank=True, default="")  # 行 9
    cover = models.ImageField(upload_to="covers/", null=True, blank=True)  # 行 10

    is_published = models.BooleanField(default=True)  # 行 12
    created_at = models.DateTimeField(auto_now_add=True)  # 行 13
    updated_at = models.DateTimeField(auto_now=True)  # 行 14

    class Meta:  # 行 16
        ordering = ["-created_at"]

    def __str__(self):  # 行 19
        return self.title


# 行 23
class Chapter(models.Model):
    book = models.ForeignKey(Book, related_name="chapters", on_delete=models.CASCADE)  # 行 24
    title = models.CharField(max_length=200)  # 行 25
    order = models.PositiveIntegerField()  # 行 26
    content = models.TextField()  # 行 27

    created_at = models.DateTimeField(auto_now_add=True)  # 行 29
    updated_at = models.DateTimeField(auto_now=True)  # 行 30

    class Meta:  # 行 32
        ordering = ["order"]
        unique_together = ("book", "order")  # 同一本书章节序号不能重复

    def __str__(self):  # 行 36
        return f"{self.book.title} - {self.order}. {self.title}"


# 行 40
class Bookshelf(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="shelf_items", on_delete=models.CASCADE)  # 行 41
    book = models.ForeignKey(Book, related_name="in_shelves", on_delete=models.CASCADE)  # 行 42

    # 记录阅读进度（可选，但很有用）
    last_read_chapter = models.ForeignKey(
        Chapter, null=True, blank=True, on_delete=models.SET_NULL, related_name="last_read_by"  # 行 46
    )
    last_read_at = models.DateTimeField(null=True, blank=True)  # 行 48

    added_at = models.DateTimeField(auto_now_add=True)  # 行 50

    class Meta:  # 行 52
        unique_together = ("user", "book")  # 同一用户同一本书只能加入一次
        ordering = ["-added_at"]

    def __str__(self):  # 行 56
        return f"{self.user.username} - {self.book.title}"


class ReadingBookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reading_bookmarks", on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name="reading_bookmarks", on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, related_name="reading_bookmarks", on_delete=models.CASCADE)
    note = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "chapter")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} bookmark {self.chapter_id}"
