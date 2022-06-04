from __future__ import annotations

from collections.abc import Iterable, Mapping, AsyncGenerator
from typing import Optional, Any

from .request import Request
from .response import Status, Response
from .utils.json import to_json


class ExceptionResponse(BaseException, Response):
    """
    Base exception response class that its status code and other parameters must be set manually.
    Also, by expanding this class, you can create all kinds of error responses.

    :ivar body: The HTTP response body
    :ivar status: The HTTP response status
    :ivar headers: The HTTP response headers
    :ivar content_type: The HTTP response content type
    :ivar compress: Determines whether or not to compress (gzip) the response
    """
    def __init__(
            self,
            body: Any,
            status: Status = Status.OK,
            headers: Optional[Iterable[[bytes, bytes]]] = None,
            content_type: bytes = b'text/plain',
            compress: bool = False) -> None:
        BaseException.__init__(self)
        """
        Initialize instance.

        :param body: The HTTP response body
        :param status: The HTTP response status
        :param headers: The HTTP response headers
        :param content_type: The HTTP response content type
        :param compress: Determines whether or not to compress (gzip) the response
        """
        Response.__init__(
            self,
            body=body,
            status=status,
            headers=headers,
            content_type=content_type,
            compress=compress)

    async def __call__(self, request: Request) \
            -> tuple[bytes | AsyncGenerator[bytes],
                     int,
                     list[[bytes, bytes]],
                     bool]:
        """
        Generate and return response data when the Response object is called.

        :param request: :class:`~backendpy.request.Request` class instance
        :return: Tuple of generated response info
        """
        return await super().__call__(request)


class BadRequest(ExceptionResponse):
    """
    Bad request error response class
    inherited from :class:`~backendpy.exception.ExceptionResponse` class.
    """

    def __init__(
            self,
            body: Any = Status.BAD_REQUEST.description,
            content_type: Optional[bytes] = None) -> None:
        super().__init__(
            body=body if not isinstance(body, Mapping) else to_json(body),
            status=Status.BAD_REQUEST,
            content_type=content_type if content_type else
            (b'text/plain' if not isinstance(body, Mapping) else b'application/json'))


class Unauthorized(ExceptionResponse):
    """
    Unauthorized request error response class
    inherited from :class:`~backendpy.exception.ExceptionResponse` class.
    """

    def __init__(
            self,
            body: Any = Status.UNAUTHORIZED.description,
            content_type: Optional[bytes] = None) -> None:
        super().__init__(
            body=body if not isinstance(body, Mapping) else to_json(body),
            status=Status.UNAUTHORIZED,
            content_type=content_type if content_type else
            (b'text/plain' if not isinstance(body, Mapping) else b'application/json'))


class Forbidden(ExceptionResponse):
    """
    Forbidden request error response class
    inherited from :class:`~backendpy.exception.ExceptionResponse` class.
    """

    def __init__(
            self,
            body: Any = Status.FORBIDDEN.description,
            content_type: Optional[bytes] = None) -> None:
        super().__init__(
            body=body if not isinstance(body, Mapping) else to_json(body),
            status=Status.FORBIDDEN,
            content_type=content_type if content_type else
            (b'text/plain' if not isinstance(body, Mapping) else b'application/json'))


class NotFound(ExceptionResponse):
    """
    Resource not found error response class
    inherited from :class:`~backendpy.exception.ExceptionResponse` class.
    """

    def __init__(
            self,
            body: Any = Status.NOT_FOUND.description,
            content_type: Optional[bytes] = None) -> None:
        super().__init__(
            body=body if not isinstance(body, Mapping) else to_json(body),
            status=Status.NOT_FOUND,
            content_type=content_type if content_type else
            (b'text/plain' if not isinstance(body, Mapping) else b'application/json'))


class ServerError(ExceptionResponse):
    """
    Server error response class
    inherited from :class:`~backendpy.exception.ExceptionResponse` class.
    """

    def __init__(
            self,
            body: Any = Status.INTERNAL_SERVER_ERROR.description,
            content_type: Optional[bytes] = None) -> None:
        super().__init__(
            body=body if not isinstance(body, Mapping) else to_json(body),
            status=Status.INTERNAL_SERVER_ERROR,
            content_type=content_type if content_type else
            (b'text/plain' if not isinstance(body, Mapping) else b'application/json'))
