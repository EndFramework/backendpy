from __future__ import annotations

from collections.abc import Mapping, Iterable, AsyncGenerator
from typing import Optional, Any

from .request import Request
from .exception import ExceptionResponse
from .response import Status, JSON


class Error(ExceptionResponse, JSON):
    def __init__(
            self, code: int,
            message_data: Optional[Mapping[str, Any] |
                                   Iterable[Any] |
                                   Any] = None,
            data: Optional[Any] = None,
            headers: Optional[Iterable[[bytes, bytes]]] = None,
            compress: bool = False) -> None:
        JSON.__init__(self, body=None, headers=headers, compress=compress)
        self.code = code
        self.message_data = message_data
        self.data = data

    async def __call__(self, request: Request) \
            -> tuple[bytes | AsyncGenerator[bytes],
                     int,
                     list[[bytes, bytes]],
                     bool]:
        error = request.app.errors[self.code]
        self.status = error.status
        self.body = {
            'status': 'error',
            'code': self.code}

        if self.message_data:
            if isinstance(self.message_data, Mapping):
                self.body['message'] = error.message.format(**self.message_data)
            elif isinstance(self.message_data, Iterable):
                self.body['message'] = error.message.format(*self.message_data)
            else:
                self.body['message'] = error.message.format(self.message_data)
        else:
            self.body['message'] = error.message

        if self.data is not None:
            self.body['data'] = self.data

        return await JSON.__call__(self, request)


class ErrorCode:
    def __init__(self, code: int, message: str, status: Status) -> None:
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


class ErrorList:
    def __init__(self, *codes: ErrorCode) -> None:
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
    ErrorCode(1002, "Unexpected data", Status.BAD_REQUEST),)
