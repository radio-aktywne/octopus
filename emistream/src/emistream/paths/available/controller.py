from starlite import Controller, WebSocket, get, websocket
from websockets.exceptions import ConnectionClosedError

from emistream.models.available import (
    AvailableNotification,
    AvailableResponse,
)
from emistream.stream import manager


class AvailableController(Controller):
    path = None

    @get()
    def available(self) -> AvailableResponse:
        return AvailableResponse(availability=manager.availability())

    @websocket("/notify")
    async def notify_available(self, socket: WebSocket) -> None:
        await socket.accept()
        try:
            while True:  # TODO: fix shutdown
                await manager.availability_changed()
                availability = manager.availability()
                notification = AvailableNotification(availability=availability)
                await socket.send_json(notification.json())
        finally:
            try:
                await socket.close()
            except ConnectionClosedError:
                pass
