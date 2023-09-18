from litestar.datastructures import State as LitestarState

from emistream.config import Config
from emistream.stream.state import StreamState


class State(LitestarState):
    """Use this class as a type hint for the state of your application.

    Attributes:
        config: The configuration for the application.
        stream_controller: The stream controller.
    """

    config: Config
    stream: StreamState
