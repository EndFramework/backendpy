from __future__ import annotations

from collections.abc import Mapping, Iterable, AsyncGenerator
from typing import Optional, Any

from .exception import ExceptionResponse
from .request import Request
from .response import Status, JSON


class Error(ExceptionResponse, JSON):
    """
    Predefined error response class.

    :ivar code: Predefined error code number
    :ivar message_data: Values used for error message formatting
    :ivar data: Error related data with a structure supported by JSON format
    :ivar headers: The HTTP response headers
    :ivar compress: Determines whether or not to compress (gzip) the response
    """

    def __init__(
            self,
            code: int,
            message_data: Optional[Mapping[str, Any] |
                                   Iterable[Any] |
                                   Any] = None,
            data: Optional[Any] = None,
            headers: Optional[Iterable[[bytes, bytes]]] = None,
            compress: bool = False) -> None:
        """
        Initialize instance.

        :param code: Predefined error code number
        :param message_data: Values used for error message formatting
        :param data: Error related data with a structure supported by JSON format
        :param headers: The HTTP response headers
        :param compress: Determines whether or not to compress (gzip) the response
        """
        JSON.__init__(self, body=None, headers=headers, compress=compress)
        self.code = code
        self.message_data = message_data
        self.data = data

    async def __call__(self, request: Request) \
            -> tuple[bytes | AsyncGenerator[bytes],
                     int,
                     list[[bytes, bytes]],
                     bool]:
        """
        Return error data when the error object is raised.

        :param request: :class:`~backendpy.request.Request` class instance
        :return: Tuple of generated error response info
        """
        error = request.app.errors[self.code]
        self.status = error.status
        self.body = error.as_dict()

        if self.message_data:
            if isinstance(self.message_data, Mapping):
                self.body['message'] = self.body['message'].format(**self.message_data)
            elif isinstance(self.message_data, Iterable):
                self.body['message'] = self.body['message'].format(*self.message_data)
            else:
                self.body['message'] = self.body['message'].format(self.message_data)

        if self.data is not None:
            self.body['data'] = self.data

        return await JSON.__call__(self, request)


class ErrorCode:
    """A class to define error response item."""

    def __init__(self, code: int, message: str, status: Status) -> None:
        """
        Initialize instance.

        :param code: The error number
        :param message: The error message string
        :param status: HTTP response status
        """
        self._code: int = code
        self._message: str = message
        self._status: Status = status

    @property
    def code(self) -> int:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    @property
    def status(self) -> Status:
        return self._status

    def as_dict(self) -> dict:
        return {'status': 'error',
                'code': self._code,
                'message': self._message}


class ErrorList:
    """Container class to define list of the :class:`~backendpy.error.ErrorCode`."""

    def __init__(self, *codes: ErrorCode) -> None:
        """
        Initialize ErrorList instance.

        :param codes: Instances of the :class:`~backendpy.error.ErrorCode` class as arguments
        """
        self._items: dict[int, ErrorCode] = dict()
        self.extend(*codes)

    @property
    def items(self) -> dict[int, ErrorCode]:
        """Get items"""
        return self._items

    def extend(self, *codes: ErrorCode) -> None:
        """Extend items"""
        for i in codes:
            if not isinstance(i, ErrorCode):
                raise Exception('Invalid error code type')
            if i.code in self._items:
                raise Exception(f'Duplicate error code "{i.code}"')
            self._items[i.code] = i

    def merge(self, other: ErrorList) -> None:
        """Merge items from another ErrorList class instance with this instance."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"{type(self.__class__)} and {type(other)} cannot be merged.")
        for code, i in other.items.items():
            if code in self._items:
                raise Exception(f'Duplicate error code "{code}"')
            self._items[code] = i

    def __getitem__(self, item) -> ErrorCode:
        return self._items[item]


base_errors = ErrorList(
    ErrorCode(1000, "Server error", Status.INTERNAL_SERVER_ERROR),
    ErrorCode(1001, "Not found", Status.NOT_FOUND),
    ErrorCode(1002, "Unexpected data", Status.BAD_REQUEST),
    ErrorCode(1003, "Disallowed host", Status.BAD_REQUEST),)
