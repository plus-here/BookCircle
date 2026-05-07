from django.urls import path
from .views import ActivityListCreateView, ActivityDetailView

urlpatterns = [
    # 管理端：活动列表 + 新建
    path("admin/activities/", ActivityListCreateView.as_view()),
    # 管理端：活动详情 + 修改 + 删除（你的 ActivityDetailView 一般支持 GET/PATCH/DELETE）
    path("admin/activities/<int:pk>/", ActivityDetailView.as_view()),
]
