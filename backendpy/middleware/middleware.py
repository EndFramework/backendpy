from ..app import Backendpy
from ..request import Request
from ..response.response import Response


class Middleware:

    @staticmethod
    def process_application(application: Backendpy):
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
