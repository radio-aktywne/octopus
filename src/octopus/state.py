from litestar.datastructures import State as LitestarState
from pylocks.base import Lock
from pystores.base import Store

from octopus.config.models import Config
from octopus.services.apis.beaver.service import BeaverService
from octopus.services.streaming.models import Instance


class State(LitestarState):
    """Use this class as a type hint for the state of the service."""

    beaver: BeaverService
    """Service for beaver API."""

    config: Config
    """Configuration for the service."""

    lock: Lock
    """Lock for the store."""

    store: Store[Instance | None]
    """Store for the state of currently streamed instance."""
