from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from panel import urls as echo_routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            echo_routing.websocket_urlpatterns
        )
    )
})
