from starlite import Controller, State, WebSocket, get, websocket
from websockets.exceptions import ConnectionClosedError

from emistream.models.available import AvailableNotification, AvailableResponse


class AvailableController(Controller):
    path = None

    @get()
    async def available(self, state: State) -> AvailableResponse:
        return AvailableResponse(
            availability=await state.stream_manager.availability()
        )

    @websocket("/notify")
    async def notify_available(self, state: State, socket: WebSocket) -> None:
        await socket.accept()
        try:
            previous = None
            while True:
                await state.stream_manager.state_changed()
                availability = await state.stream_manager.availability()
                if availability != previous:
                    notification = AvailableNotification(
                        availability=availability
                    )
                    await socket.send_json(notification.json())
                    previous = availability
        finally:
            try:
                await socket.close()
            except ConnectionClosedError:
                pass
