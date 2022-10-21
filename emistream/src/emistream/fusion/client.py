from typing import Optional, Dict, Any

from pystreams.ffmpeg import FFmpegNode

from emistream.client import SrtClient


class FusionClient:
    def __init__(
        self,
        host: str,
        port: int,
        srt_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._srt_client = SrtClient(host, port, **(srt_kwargs or {}))

    def get_stream_node(self, **kwargs) -> FFmpegNode:
        options = {"acodec": "copy", "format": "opus"}
        return self._srt_client.get_node(**(options | kwargs))
