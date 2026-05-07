# config/urls.py
# 行 1
from django.contrib import admin
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),  # 行 10

    # 账号体系
    path("api/auth/", include("accounts.urls")),  # 行 13
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # 行 14
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # 行 15

    # 图书/书架
    path("api/", include("books.urls")),  # 行 18

    # ✅ 社团模块（你现在缺的就是这一行）
    path("api/", include("clubs.urls")),  # 行 21

    path("api/", include("groupchat.urls")),

    path("api/", include("directchat.urls")),

    path("api/", include("activities.urls")),

    path("api/", include("announcements.urls")),

    path("api/", include("accounts.admin_urls")),

    path("api/", include("activities.admin_urls")),

    path("api/", include("clubs.admin_urls")),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 行 25
