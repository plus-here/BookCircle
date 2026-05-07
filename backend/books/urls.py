# books/urls.py
# 行 1
from django.urls import path

from .views import (
    BookListView,
    BookDetailView,
    ChapterListView,
    ChapterDetailView,
    BookshelfListCreateView,
    BookshelfRemoveView,
    UpdateReadingProgressView,
    ReadingBookmarkListCreateView,
    ReadingBookmarkRemoveView,
)

from .admin_views import (
    AdminBookListCreateView, AdminBookRUDView,
    AdminChapterListCreateView, AdminChapterRUDView,
)

urlpatterns = [
    path("books/", BookListView.as_view(), name="book_list"),                    # 行 16
    path("books/<int:pk>/", BookDetailView.as_view(), name="book_detail"),       # 行 17
    path("books/<int:book_id>/chapters/", ChapterListView.as_view(), name="chapter_list"),  # 行 18
    path("chapters/<int:pk>/", ChapterDetailView.as_view(), name="chapter_detail"),        # 行 19

    path("shelf/", BookshelfListCreateView.as_view(), name="shelf_list_create"),          # 行 21
    path("shelf/<int:book_id>/", BookshelfRemoveView.as_view(), name="shelf_remove"),     # 行 22
    path("shelf/progress/", UpdateReadingProgressView.as_view(), name="shelf_progress"),  # 行 23
    path("bookmarks/", ReadingBookmarkListCreateView.as_view(), name="bookmark_list_create"),
    path("bookmarks/<int:pk>/", ReadingBookmarkRemoveView.as_view(), name="bookmark_remove"),

    path("admin/books/", AdminBookListCreateView.as_view()),
    path("admin/books/<int:pk>/", AdminBookRUDView.as_view()),
    path("admin/chapters/", AdminChapterListCreateView.as_view()),
    path("admin/chapters/<int:pk>/", AdminChapterRUDView.as_view()),
]
