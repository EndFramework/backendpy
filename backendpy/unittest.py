import asyncio
import functools
import unittest


class AsyncTestCase(unittest.TestCase):
    """Subclass of :class:`unittest.TestCase` with added async functionality."""

    def __init__(self, methodName: str = 'runTest'):
        self._event_loop = asyncio.get_event_loop()
        super().__init__(methodName=methodName)

    def async_test(self, coro):
        @functools.wraps(coro)
        def wrapper(*args, **kwargs):
            self._event_loop.run_until_complete(coro(*args, **kwargs))
        return wrapper

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if asyncio.iscoroutinefunction(attr):
            return self.async_test(attr)
        return attr


class TestCase(unittest.TestCase):
    """Subclass of :class:`unittest.TestCase`."""

    def __init__(self, methodName: str = 'runTest'):
        super().__init__(methodName=methodName)

