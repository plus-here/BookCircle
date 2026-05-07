from django.urls import re_path
from .consumers import DirectChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/dm/(?P<thread_id>\d+)/$", DirectChatConsumer.as_asgi()),
]
