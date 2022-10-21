import json

from starlite import Controller, State, WebSocket, get

from emistream.api.paths.available.models import (
    AvailableResponse,
    AvailableStreamResponse,
)
from emistream.api.socket import websocket


class AvailableController(Controller):
    path = None

    @get()
    async def available(self, state: State) -> AvailableResponse:
        return AvailableResponse(
            availability=await state.stream_manager.availability()
        )

    @websocket("/watch")
    async def watch_available(self, state: State, socket: WebSocket) -> None:
        previous = None
        while True:
            await state.stream_manager.state_changed()
            availability = await state.stream_manager.availability()
            if availability != previous:
                response = AvailableStreamResponse(availability=availability)
                await socket.send_json(json.loads(response.json()))
                previous = availability
