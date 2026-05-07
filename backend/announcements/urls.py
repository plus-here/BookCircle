from django.urls import path
from .views import (
    AnnouncementPublicListView,
    AnnouncementPublicDetailView,
    AnnouncementAdminListCreateView,
    AnnouncementAdminRUDView,
    AdminStatsView,
    AdminUploadView,
)

urlpatterns = [
    path("announcements/", AnnouncementPublicListView.as_view()),
    path("announcements/<int:pk>/", AnnouncementPublicDetailView.as_view()),

    path("admin/announcements/", AnnouncementAdminListCreateView.as_view()),
    path("admin/announcements/<int:pk>/", AnnouncementAdminRUDView.as_view()),

    path("admin/stats/", AdminStatsView.as_view()),

    path("admin/uploads/", AdminUploadView.as_view()),

]
