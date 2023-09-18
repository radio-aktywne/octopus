from collections.abc import Iterable
from typing import TextIO

from omegaconf import OmegaConf
from yaml import YAMLError

from emistream.builder import Builder
from emistream.config.errors import ConfigParseError
from emistream.config.models import Config


class ConfigBuilder(Builder[Config]):
    """Builds the config.

    Args:
        file: File-like object to load config from.
        overrides: Config overrides in the form of a dotlist.
    """

    def __init__(
        self,
        file: TextIO | None = None,
        overrides: Iterable[str] | None = None,
    ) -> None:
        self._file = file
        self._overrides = overrides

    def build(self) -> Config:
        try:
            config = OmegaConf.create()
            if self._file is not None:
                config = OmegaConf.merge(config, OmegaConf.load(self._file))
            if self._overrides is not None:
                config = OmegaConf.merge(
                    config, OmegaConf.from_dotlist(list(self._overrides))
                )
            config = OmegaConf.to_container(config, resolve=True)
            return Config.parse_obj(config)
        except (ValueError, YAMLError) as e:
            raise ConfigParseError from e
