# clubs/urls.py
from django.urls import path
from .views import (
    ClubListView,
    ClubDetailView,
    ClubSectionListView,
    ClubMemberListView,
    ClubMeView,
    JoinClubView,
    JoinRequestListView,
    ApproveJoinRequestView,
    SectionPostListCreateView,
    PostDetailView,
    CommentListCreateView,
)

urlpatterns = [
    path("clubs/", ClubListView.as_view()),
    path("clubs/<int:pk>/", ClubDetailView.as_view()),
    path("clubs/<int:club_id>/sections/", ClubSectionListView.as_view()),
    path("clubs/<int:club_id>/members/", ClubMemberListView.as_view()),

    path("clubs/<int:club_id>/me/", ClubMeView.as_view()),
    path("clubs/<int:club_id>/join/", JoinClubView.as_view()),
    path("clubs/<int:club_id>/requests/", JoinRequestListView.as_view()),
    path("requests/<int:request_id>/<str:action>/", ApproveJoinRequestView.as_view()),

    path("sections/<int:section_id>/posts/", SectionPostListCreateView.as_view()),
    path("posts/<int:pk>/", PostDetailView.as_view()),
    path("posts/<int:post_id>/comments/", CommentListCreateView.as_view()),
]
