import importlib
from .request import Request
from .response import Response


class Middleware:

    @staticmethod
    def process_application(application):
        """
        Capture application and return modified version of it.
        :param application: the Backendpy class instance in queue
        :return: Backendpy class instance
        """
        return application

    @staticmethod
    async def process_request(request: Request):
        """
        Capture request and return modified version of the request
        or raise the Response exception to end request evaluation queue.
        :param request: the Request class instance in queue
        :return: Request class instance
        """
        return request

    @staticmethod
    async def process_handler(request: Request, handler):
        """
        Capture handler and return modified version of the handler
        or raise the Response exception to end request evaluation queue.
        :param request: the Request class modified instance in queue
        :param handler: the handler function in queue
        :return: Handler function
        """
        return handler

    @staticmethod
    async def process_response(request: Request, response: Response):
        """
        Capture response and return modified version of the response
        or raise the Response exception to end response evaluation queue.
        :param request: the Request class modified instance in queue
        :param response: the Response class instance in queue
        :return: Response class instance
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
