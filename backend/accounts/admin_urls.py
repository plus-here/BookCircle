from django.urls import path
from .admin_views import AdminUserListView, AdminUserRUDView

urlpatterns = [
    path("admin/users/", AdminUserListView.as_view()),
    path("admin/users/<int:pk>/", AdminUserRUDView.as_view()),
]
