from rest_framework import generics, permissions
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from .models import Book, Chapter
from .admin_serializers import BookAdminSerializer, ChapterAdminSerializer


class AdminBookListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = BookAdminSerializer
    queryset = Book.objects.all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]


class AdminBookRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = BookAdminSerializer
    queryset = Book.objects.all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]


class AdminChapterListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ChapterAdminSerializer

    def get_queryset(self):
        qs = Chapter.objects.all().order_by("book_id", "order")
        book_id = self.request.query_params.get("book")
        if book_id:
            qs = qs.filter(book_id=book_id).order_by("order")
        return qs


class AdminChapterRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ChapterAdminSerializer
    queryset = Chapter.objects.all()
