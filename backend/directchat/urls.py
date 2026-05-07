from django.urls import path
from .views import ThreadListView, ThreadCreateView, MessageListView

urlpatterns = [
    path("dm/threads/", ThreadListView.as_view()),
    path("dm/threads/create/", ThreadCreateView.as_view()),
    path("dm/threads/<int:thread_id>/messages/", MessageListView.as_view()),
]
