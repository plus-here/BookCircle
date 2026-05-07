from django.urls import path
from .views import (
    ActivityListCreateView,
    ActivityDetailView,
    ActivitySignupCancelView,
    ActivitySignupView,
    MySignupsView,
    ActivitySignupsForClubAdminView,
)

urlpatterns = [
    path("activities/", ActivityListCreateView.as_view()),
    path("activities/<int:pk>/", ActivityDetailView.as_view()),
    path("activities/<int:pk>/signup/", ActivitySignupView.as_view()),
    path("activities/<int:pk>/signup/cancel/", ActivitySignupCancelView.as_view()),
    path("activities/my/signups/", MySignupsView.as_view()),
    path("activities/<int:pk>/signups/", ActivitySignupsForClubAdminView.as_view()),
]
