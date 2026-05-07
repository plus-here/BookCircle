# config/asgi.py
# 行 1
import os

# 行 4：必须先设置 DJANGO_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 行 7：先初始化 Django ASGI（这一步会完成 settings 加载）
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# 行 11：再导入 channels 和你的 websocket 路由（此时 settings 已就绪）
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

import groupchat.routing
import directchat.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        URLRouter(groupchat.routing.websocket_urlpatterns + directchat.routing.websocket_urlpatterns)
    ),
})
