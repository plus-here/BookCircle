# books/views.py
# 行 1
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book, Chapter, Bookshelf, ReadingBookmark
from .serializers import (
    BookListSerializer,
    BookDetailSerializer,
    ChapterListSerializer,
    ChapterDetailSerializer,
    BookshelfSerializer,
    ReadingBookmarkSerializer,
)


# 行 17
class BookListView(generics.ListAPIView):
    """
    GET /api/books/?q=关键词
    """
    serializer_class = BookListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Book.objects.filter(is_published=True)
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(author__icontains=q))
        return qs


# 行 35
class BookDetailView(generics.RetrieveAPIView):
    """
    GET /api/books/<id>/
    """
    queryset = Book.objects.filter(is_published=True)
    serializer_class = BookDetailSerializer
    permission_classes = [permissions.AllowAny]


# 行 46
class ChapterListView(generics.ListAPIView):
    """
    GET /api/books/<book_id>/chapters/
    """
    serializer_class = ChapterListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        book_id = self.kwargs["book_id"]
        return Chapter.objects.filter(book_id=book_id).order_by("order")


# 行 60
class ChapterDetailView(generics.RetrieveAPIView):
    """
    GET /api/chapters/<id>/
    """
    queryset = Chapter.objects.all()
    serializer_class = ChapterDetailSerializer
    permission_classes = [permissions.AllowAny]


# 行 71
class BookshelfListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/shelf/     我的书架列表
    POST /api/shelf/     加入书架: { "book_id": 1 }
    """
    serializer_class = BookshelfSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bookshelf.objects.filter(user=self.request.user).select_related("book", "last_read_chapter")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book_id = serializer.validated_data["book_id"]
        book = Book.objects.filter(id=book_id, is_published=True).first()
        if not book:
            return Response({"detail": "图书不存在或未发布"}, status=status.HTTP_404_NOT_FOUND)

        obj, created = Bookshelf.objects.get_or_create(user=request.user, book=book)
        out = BookshelfSerializer(obj, context={"request": request}).data
        return Response(out, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# 行 101
class BookshelfRemoveView(generics.DestroyAPIView):
    """
    DELETE /api/shelf/<book_id>/   从书架移除
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        book_id = self.kwargs["book_id"]
        deleted, _ = Bookshelf.objects.filter(user=request.user, book_id=book_id).delete()
        if deleted == 0:
            return Response({"detail": "书架中没有这本书"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


# 行 118
class UpdateReadingProgressView(generics.GenericAPIView):
    """
    PATCH /api/shelf/progress/
    Body: { "book_id": 1, "chapter_id": 10 }
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        book_id = request.data.get("book_id")
        chapter_id = request.data.get("chapter_id")

        if not book_id or not chapter_id:
            return Response({"detail": "book_id 和 chapter_id 必填"}, status=status.HTTP_400_BAD_REQUEST)

        shelf = Bookshelf.objects.filter(user=request.user, book_id=book_id).first()
        if not shelf:
            return Response({"detail": "请先把书加入书架"}, status=status.HTTP_404_NOT_FOUND)

        chapter = Chapter.objects.filter(id=chapter_id, book_id=book_id).first()
        if not chapter:
            return Response({"detail": "章节不存在"}, status=status.HTTP_404_NOT_FOUND)

        shelf.last_read_chapter = chapter
        shelf.last_read_at = timezone.now()
        shelf.save()

        out = BookshelfSerializer(shelf, context={"request": request}).data
        return Response(out, status=status.HTTP_200_OK)


class ReadingBookmarkListCreateView(APIView):
    """
    GET  /api/bookmarks/?book_id=1
    POST /api/bookmarks/  { "chapter": 10, "note": "..." }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = ReadingBookmark.objects.filter(user=request.user).select_related("book", "chapter")
        book_id = request.query_params.get("book_id")
        if book_id:
            qs = qs.filter(book_id=book_id)
        return Response(ReadingBookmarkSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        chapter_id = request.data.get("chapter")
        chapter = Chapter.objects.filter(id=chapter_id, book__is_published=True).select_related("book").first()
        if not chapter:
            return Response({"detail": "章节不存在"}, status=status.HTTP_404_NOT_FOUND)

        obj, _ = ReadingBookmark.objects.update_or_create(
            user=request.user,
            chapter=chapter,
            defaults={
                "book": chapter.book,
                "note": request.data.get("note", ""),
            },
        )
        return Response(ReadingBookmarkSerializer(obj).data, status=status.HTTP_201_CREATED)


class ReadingBookmarkRemoveView(APIView):
    """
    DELETE /api/bookmarks/<id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        deleted, _ = ReadingBookmark.objects.filter(id=pk, user=request.user).delete()
        if deleted == 0:
            return Response({"detail": "书签不存在"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
