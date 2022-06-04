import importlib

from .request import Request
from .response import Response


class Middleware:

    @staticmethod
    def process_application(application):
        """
        Take instance of :class:`~backendpy.Backendpy` class and return modified version of it.
        :param application: :class:`~backendpy.Backendpy` class instance (Received from the middlewares queue)
        :return: Modified :class:`~backendpy.Backendpy` class instance
        """
        return application

    @staticmethod
    async def process_request(request: Request):
        """
        Take a :class:`~backendpy.request.Request` object before it reaches the handler layer and return a processed
        or modified version of it or interrupt the execution of the request with raise an exception response.
        :param request: :class:`~backendpy.request.Request` class instance (Received from the middlewares queue)
        :return: Modified :class:`~backendpy.request.Request` class instance
        """
        return request

    @staticmethod
    async def process_handler(request: Request, handler):
        """
        Take a request handler (which is an async function) before executing it and return a modified version of it
        or interrupt the execution of the request with raise an exception response.
        :param request: :class:`~backendpy.request.Request` class instance (Received from the middlewares queue)
        :param handler: Async handler function (Received from the middlewares queue)
        :return: Modified handler function
        """
        return handler

    @staticmethod
    async def process_response(request: Request, response: Response):
        """
        Capture the :class:`~backendpy.response.Response` object before sending it to the client and return a
        processed, modified, or replaced Response object or interrupt the execution of the request with raise an
        exception response.
        :param request: :class:`~backendpy.request.Request` class instance (Received from the middlewares queue)
        :param response: :class:`~backendpy.response.Response` class instance (Received from the middlewares queue)
        :return: Modified :class:`~backendpy.response.Response` class instance
        """
        return response


class MiddlewareProcessor:

    def __init__(self, paths=None):
        self._middlewares_paths = paths if paths else []
        self._middlewares = []

    @property
    def middlewares(self):
        if not self._middlewares:
            for m in self._middlewares_paths:
                module_name, class_name = m.rsplit('.', 1)
                self._middlewares.append(getattr(importlib.import_module(module_name), class_name)())
        return self._middlewares

    def run_process_application(self, application):
        for middleware in self.middlewares:
            application = middleware.process_application(application)
        return application

    async def run_process_request(self, request):
        for middleware in self.middlewares:
            request = await middleware.process_request(request)
        return request

    async def run_process_handler(self, request, handler):
        for middleware in self.middlewares:
            handler = await middleware.process_handler(request, handler)
        return handler

    async def run_process_response(self, request, response):
        for middleware in reversed(self.middlewares):
            response = await middleware.process_response(request, response)
        return response
