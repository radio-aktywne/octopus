from typing import Iterable, Optional, TextIO, Tuple

from omegaconf import OmegaConf
from pydantic import Extra
from pydantic.env_settings import BaseSettings, SettingsSourceCallable

from emistream import resource_text


class BaseConfig(BaseSettings):
    class Config:
        env_prefix = "emistream_"
        env_nested_delimiter = "__"
        env_file = ".env"
        extra = Extra.allow

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings


class Config(BaseConfig):
    host: str = "0.0.0.0"
    port: int = 10000
    live_host: str = "localhost"
    live_port: int = 9000
    recording_host: str = "localhost"
    recording_port: int = 31000


def get_config(
    f: Optional[TextIO] = None, overrides: Optional[Iterable[str]] = None
) -> Config:
    config = OmegaConf.create(resource_text("config.yaml"))
    if f is not None:
        config = OmegaConf.merge(config, OmegaConf.load(f))
    if overrides is not None:
        config = OmegaConf.merge(
            config, OmegaConf.from_dotlist(list(overrides))
        )
    config = OmegaConf.to_container(config, resolve=True)
    return Config.parse_obj(config)
