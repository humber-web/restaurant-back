import asyncio
from django.db import connection
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

async def listen_to_db():
    channel_layer = get_channel_layer()
    with connection.cursor() as cursor:
        cursor.execute("LISTEN order_channel;")
        while True:
            connection.connection.poll()
            while connection.connection.notifies:
                notify = connection.connection.notifies.pop(0)
                await channel_layer.group_send("orders", {
                    'type': 'send_order_update',
                    'message': notify.payload,
                })
            await asyncio.sleep(1)
