from typing import Optional, Dict, Any

from pystreams.ffmpeg import FFmpegNode

from emistream.client import HttpClient, SrtClient
from emistream.recorder.models.api import RecordRequest, RecordResponse
from emistream.recorder.models.data import Event, Token


class RawRecorderClient:
    def __init__(
        self,
        host: str,
        port: int,
        secure: bool = False,
        http_kwargs: Optional[Dict[str, Any]] = None,
        srt_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._http_client = HttpClient(
            host, port, secure, **(http_kwargs or {})
        )
        self._srt_client = SrtClient(host, port, **(srt_kwargs or {}))

    async def record(self, request: RecordRequest) -> RecordResponse:
        response = await self._http_client.post("record", request.json_dict())
        return RecordResponse(**response)

    def get_stream_node(self, **kwargs) -> FFmpegNode:
        options = {"acodec": "copy", "format": "opus"}
        return self._srt_client.get_node(**(options | kwargs))


class RecorderClient:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._client = RawRecorderClient(*args, **kwargs)

    async def record(self, event: Event) -> Token:
        request = RecordRequest(event=event)
        response = await self._client.record(request)
        return response.token

    def get_stream_node(self, **kwargs) -> FFmpegNode:
        return self._client.get_stream_node(**kwargs)
