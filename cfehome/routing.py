from django.conf.urls import url
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from chat.consumer import ThreadConsumer
from chat.consumer import UserConsumer


application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path("", UserConsumer),
                    path("<int:thread_id>/", ThreadConsumer),
                ]
            )
        )
    )
})
