from django.urls import path
from .admin_views import (
    AdminClubListCreateView,
    AdminClubDetailView,
    AdminClubSectionListCreateView,
    AdminSectionDetailView,
    AdminJoinRequestListView,
)

urlpatterns = [
    path("admin/clubs/", AdminClubListCreateView.as_view()),
    path("admin/clubs/<int:pk>/", AdminClubDetailView.as_view()),

    path("admin/clubs/<int:club_id>/sections/", AdminClubSectionListCreateView.as_view()),
    path("admin/sections/<int:pk>/", AdminSectionDetailView.as_view()),

    path("admin/clubs/<int:club_id>/requests/", AdminJoinRequestListView.as_view()),
]
