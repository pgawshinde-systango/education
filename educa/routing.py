from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

'''
    You can define the root application by adding the ASGI_APPLICATION
    setting to your project. This is similar to the ROOT_URLCONF setting that points to the
    base URL patterns of your project. You can place the root application anywhere in
    your project, but it is recommended to put it in a project-level file named routing.
    py .
'''


'''
    ProtocolTypeRouter router automatically maps HTTP requests to
    the standard Django views if no specific http mapping is provided.
'''
'''
    The AuthMiddlewareStack class provided by Channels
    supports standard Django authentication, where the
    user details are stored in the session. You plan to
    access the user instance in the scope of the consumer
    to identify the user who sends a message.
'''
'''
    URLRouter to map websocket connections to the URL patterns
    defined in the websocket_urlpatterns list of the chat
    application routing file.
'''
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
