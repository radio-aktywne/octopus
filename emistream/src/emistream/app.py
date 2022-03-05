from starlite import Starlite

from emistream.paths.router import router

app = Starlite(route_handlers=[router])
