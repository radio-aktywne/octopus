import os

from pydantic import BaseModel


class Config(BaseModel):
    port: int = int(os.getenv("EMISTREAM_PORT", 10000))
    live_host: str = os.getenv("EMISTREAM_LIVE_HOST", "localhost")
    live_port: int = int(os.getenv("EMISTREAM_LIVE_PORT", 9000))
    recording_host: str = os.getenv("EMISTREAM_RECORDING_HOST", "localhost")
    recording_port: int = int(os.getenv("EMISTREAM_RECORDING_PORT", 31000))


config = Config()
