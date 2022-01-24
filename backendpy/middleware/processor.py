import importlib


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
