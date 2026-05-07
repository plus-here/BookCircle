from django.urls import path
from .views import GroupListCreateView, GroupJoinView, GroupLeaveView, GroupMessageListView

urlpatterns = [
    path("groups/", GroupListCreateView.as_view()),
    path("groups/<int:group_id>/join/", GroupJoinView.as_view()),
    path("groups/<int:group_id>/leave/", GroupLeaveView.as_view()),
    path("groups/<int:group_id>/messages/", GroupMessageListView.as_view()),
]
