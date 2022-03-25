import asyncio
from typing import Callable, TypeVar
from uuid import uuid4

T = TypeVar("T")


def generate_uuid() -> str:
    return uuid4().hex


async def thread(f: Callable[..., T]) -> T:
    return await asyncio.get_running_loop().run_in_executor(None, f)
