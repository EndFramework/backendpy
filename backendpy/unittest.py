import unittest
import asyncio
import functools
from .helpers import http


class AsyncTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        self.client = http.AsyncHttpClient()
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
    def __init__(self, methodName='runTest'):
        self.client = http.HttpClient()
        super().__init__(methodName=methodName)
