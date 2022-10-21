from pydantic import BaseModel

from emistream.config.base import BaseConfig


class FusionConfig(BaseModel):
    host: str = "localhost"
    port: int = 9000


class EmirecorderConfig(BaseModel):
    host: str = "localhost"
    port: int = 31000


class Config(BaseConfig):
    host: str = "0.0.0.0"
    port: int = 10000
    fusion: FusionConfig = FusionConfig()
    emirecorder: EmirecorderConfig = EmirecorderConfig()
    timeout: int = 60
