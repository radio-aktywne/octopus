from uuid import UUID

from litestar.datastructures import State as LitestarState
from pylocks.base import Lock
from pystores.base import Store

from octopus.config.models import Config
from octopus.services.beaver.service import BeaverService


class State(LitestarState):
    """Use this class as a type hint for the state of the service."""

    beaver: BeaverService
    """Service for beaver service."""

    config: Config
    """Configuration for the service."""

    lock: Lock
    """Lock for the store."""

    store: Store[UUID | None]
    """Store for the state of currently streamed event."""
