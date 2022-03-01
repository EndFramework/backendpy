from __future__ import annotations

from collections.abc import Iterable, Mapping, AsyncGenerator
from typing import Optional, Any

from .request import Request
from .response import Status, Response
from .utils.json import to_json


class ExceptionResponse(BaseException, Response):
    def __init__(
            self,
            body: Any,
            status: Status = Status.OK,
            headers: Optional[Iterable[[bytes, bytes]]] = None,
            content_type: bytes = b'text/plain',
            compress: bool = False) -> None:
        BaseException.__init__(self)
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
        return await super().__call__(request)


class BadRequest(ExceptionResponse):
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
    def __init__(
            self,
            body: Any = Status.INTERNAL_SERVER_ERROR.description,
            content_type: Optional[bytes] = None) -> None:
        super().__init__(
            body=body if not isinstance(body, Mapping) else to_json(body),
            status=Status.INTERNAL_SERVER_ERROR,
            content_type=content_type if content_type else
            (b'text/plain' if not isinstance(body, Mapping) else b'application/json'))
