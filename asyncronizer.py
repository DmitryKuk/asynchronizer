import asyncio
import functools
import threading
from typing import Any, Callable, Optional

from _asyncronizer import Thread, IoContext, ErrorCategory, ErrorCode


__all__ = ['Thread', 'IoContext', 'ErrorCategory', 'ErrorCode', 'call_async']


def call_async(
        start_task: Callable[[Callable[..., None]], None],
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
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

    :param loop: Asyncio event loop
    :type loop: Optional[asyncio.AbstractEventLoop]

    :param default: Default result which will be set as feature result
    :type default: Any

    :param pack_single: Force single result packing as tuple
    :type pack_single: bool

    :return: Feature associated with started asynchronous operation result
    :rtype: asyncio.Feature
    """

    if loop is None:
        loop = asyncio.get_event_loop()

    ready_queue = __get_ready_queue(loop)
    future = loop.create_future()
    start_task(ready_queue.prepare(future=future, default=default, pack_single=pack_single))
    return future


class __ReadyQueue:
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop
        self.__lock = threading.Lock()
        self.__ready_callbacks = set()
        self.__ready = []
        self.__set_results_job = None

    def prepare(self, future: asyncio.Future, default: Any, pack_single: bool) -> Callable[..., None]:
        on_ready = functools.partial(self.__on_ready, future=future, default=default, pack_single=pack_single)
        future.add_done_callback(lambda _future: self.__ready_callbacks.discard(on_ready))
        self.__ready_callbacks.add(on_ready)
        return on_ready

    def __on_ready(self, *result: Any, future: asyncio.Future, default: Any, pack_single: bool) -> None:
        if result:
            if not pack_single:
                result = result[0]
        else:
            result = default

        with self.__lock:
            self.__ready.append((future, result))
            if self.__set_results_job is None:
                self.__set_results_job = asyncio.run_coroutine_threadsafe(self.__set_results(), loop=self.loop)

    async def __set_results(self) -> None:
        with self.__lock:
            for future, result in self.__ready:
                future.set_result(result)

            self.__ready.clear()
            self.__set_results_job = None


def __get_ready_queue(loop: asyncio.AbstractEventLoop) -> __ReadyQueue:
    ready_queue = __ready_queues.get(loop)
    if ready_queue is None:
        ready_queue = __ReadyQueue(loop=loop)
        __ready_queues[loop] = ready_queue
    return ready_queue


__ready_queues = {}
