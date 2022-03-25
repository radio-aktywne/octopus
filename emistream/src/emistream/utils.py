import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from typing import Awaitable, Callable, TypeVar
from uuid import uuid4

T = TypeVar("T")


def generate_uuid() -> str:
    return uuid4().hex


async def thread(f: Callable[..., T]) -> T:
    return await asyncio.get_running_loop().run_in_executor(None, f)


def run_in_thread(f: Awaitable[T]) -> T:
    def run(f: Awaitable[T]) -> T:
        return asyncio.run(f)

    with ThreadPoolExecutor() as executor:
        future = executor.submit(run, f)
        return future.result()


def start_in_thread(f: Awaitable[T]) -> None:
    def run(f: Awaitable[T]) -> T:
        return asyncio.run(f)

    Thread(target=run, args=(f,)).start()
