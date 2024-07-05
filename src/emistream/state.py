from uuid import UUID

from litestar.datastructures import State as LitestarState
from pylocks.base import Lock
from pystores.base import Store

from emistream.config.models import Config
from emistream.emirecords.service import EmirecordsService
from emistream.emishows.service import EmishowsService


class State(LitestarState):
    """Use this class as a type hint for the state of your application.

    Attributes:
        config: Configuration for the application.
        emishows: Service for emishows API.
        emirecords: Service for emirecords API.
        store: Store for the state of currently streamed event.
        lock: Lock for the store.
    """

    config: Config
    emishows: EmishowsService
    emirecords: EmirecordsService
    store: Store[UUID | None]
    lock: Lock
