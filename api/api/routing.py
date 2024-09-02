from django.urls import path
from core.consumers import OrderConsumer  # Import your consumer from the correct app

websocket_urlpatterns = [
    path('ws/orders/', OrderConsumer.as_asgi()),
]
