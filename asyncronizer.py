import asyncio
import concurrent.futures
import functools
import threading
from typing import Any, Callable, Optional, MutableSet, List, Tuple

from _asyncronizer_ext import Thread, IoContext, ErrorCategory, ErrorCode


__all__ = ['Thread', 'IoContext', 'ErrorCategory', 'ErrorCode', 'Asyncronizer']


class Asyncronizer:
    def __init__(
            self,
            loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        """

        :param loop: Asyncio event loop
        :type loop: Optional[asyncio.AbstractEventLoop]
        """

        if loop is None:
            loop = asyncio.get_event_loop()

        self._loop = loop
        self._ready_queue = _ReadyQueue(loop=loop)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    def call_async(
            self,
            start_task: Callable[[Callable[..., None]], None],
            *,
            default: Any = None,
            pack_single: bool = False,
    ) -> asyncio.Future:
        """
        Wraps Boost.Asio async function for use with Python asyncio awaitable features.

        Example 1:
            // C++. Calls `on_ready(error_code)` on complete
            void async_fn(
                std::shared_ptr<boost::asio::io_context> io_context_ptr,
                std::function<void (const boost::error_code &) on_ready
            );

            # Python. Calls `async_fn` with some arguments
            async def another_fn():
                io_context = make_io_context()
                ec = await call_async(functools.partial(async_fn, io_context))
                if ec.value == 0:
                    print('Completed successfully!')

        Example 2:
            // C++. Calls something like `on_ready(42, "Hello, world!")` on complete
            void async_fn(std::function<void (int, std::string) on_ready);

            # Python. Gets several parameters as return value
            async def another_fn():
                my_int, my_str = await call_async(async_fn)
                print(f'my_int={my_int}, my_str={my_str}')

        :param start_task: Function which should be called with some callback `on_ready(*results: Any)` as only argument
        :type start_task: Callable[[Callable[[...], None]], None]

        :param default: Default result which will be set as feature result
        :type default: Any

        :param pack_single: Force single result packing as tuple
        :type pack_single: bool

        :return: Feature associated with started asynchronous operation result
        :rtype: asyncio.Feature
        """

        future = self._loop.create_future()
        start_task(self._ready_queue.prepare(future=future, default=default, pack_single=pack_single))
        return future


class _ReadyQueue:
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop
        self._lock = threading.Lock()
        self._ready_callbacks: MutableSet[Callable[..., None]] = set()
        self._ready: List[Tuple[concurrent.futures.Future, Any]] = []
        self._set_results_job: Optional[concurrent.futures.Future] = None

    def prepare(self, future: asyncio.Future, default: Any, pack_single: bool) -> Callable[..., None]:
        on_ready = functools.partial(self._on_ready, future=future, default=default, pack_single=pack_single)
        future.add_done_callback(lambda _future: self._ready_callbacks.discard(on_ready))
        self._ready_callbacks.add(on_ready)
        return on_ready

    def _on_ready(self, *result: Any, future: asyncio.Future, default: Any, pack_single: bool) -> None:
        if result:
            if not pack_single:
                result = result[0]
        else:
            result = default

        with self._lock:
            self._ready.append((future, result))
            if self._set_results_job is None:
                self._set_results_job = asyncio.run_coroutine_threadsafe(self._set_results(), loop=self.loop)

    async def _set_results(self) -> None:
        with self._lock:
            for future, result in self._ready:
                future.set_result(result)

            self._ready.clear()
            self._set_results_job = None
