import os

from pydantic import BaseModel


class Config(BaseModel):
    port: int = os.getenv("EMISTREAM_PORT", 10000)
    target_host: str = os.getenv("EMISTREAM_TARGET_HOST", "localhost")
    target_port: int = os.getenv("EMISTREAM_TARGET_PORT", 9000)


config = Config()
