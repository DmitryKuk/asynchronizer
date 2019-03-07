import asyncio
import time
import asynctest
import random

import asyncronizer
import test_module_async_sleep


class TestAsyncSleep(asynctest.TestCase):
    def setUp(self) -> None:
        self._io_context = asyncronizer.IoContext()
        self._work_guard = self._io_context.create_work_guard()
        self._runner = self._io_context.start_runner()

    def tearDown(self) -> None:
        self._work_guard.reset()
        self._runner.join()
        self._io_context.stop()

    def test_runner_is_joinable(self) -> None:
        self.assertTrue(self._runner.joinable)

    def test_work_guard(self) -> None:
        self.assertTrue(self._work_guard.owns_work)

    def test_async_wait_lowlevel(self) -> None:
        timeout = 1

        on_ready = asynctest.MagicMock()
        timer = test_module_async_sleep.SystemTimer(io_context=self._io_context, seconds=timeout)
        timer.async_wait(on_ready=on_ready)

        time.sleep(timeout * 3)

        on_ready.assert_called_once()

        args, kwags = on_ready.call_args
        self.assertEqual(1, len(args))
        self.assertDictEqual({}, kwags)

        error_code = args[0]
        self.assertTrue(isinstance(error_code, asyncronizer.ErrorCode))
        self.assertEqual(0, error_code.value)

    async def test_async_wait_highlevel(self) -> None:
        timeout = 1

        timer = test_module_async_sleep.SystemTimer(io_context=self._io_context, seconds=timeout)
        future = asyncronizer.call_async(timer.async_wait, loop=self.loop)

        time.sleep(3)
        error_code = await future

        self.assertTrue(isinstance(error_code, asyncronizer.ErrorCode))
        self.assertEqual(0, error_code.value)

    async def test_async_wait_gather(self) -> None:
        tests = 10
        timeouts = [random.uniform(0.5, 5) for _ in range(tests)]
        timers = [
            test_module_async_sleep.SystemTimer(io_context=self._io_context, seconds=timeout)
            for timeout in timeouts
        ]

        error_codes = await asyncio.gather(
            *(asyncronizer.call_async(timer.async_wait, loop=self.loop) for timer in timers)
        )

        for timer_index, (timeout, error_code) in enumerate(zip(timeouts, error_codes)):
            with self.subTest(timer=timer_index, timeout=timeout, error_code=error_code):
                self.assertEqual(0, error_code.value)
