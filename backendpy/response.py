from __future__ import annotations

import datetime
import gzip
import os
import types
import zlib
from collections.abc import Iterable, AsyncGenerator
from enum import IntEnum
from mimetypes import guess_type
from typing import TYPE_CHECKING, Optional, Any
from urllib.parse import unquote

import aiofiles.os

from .utils.bytes import to_bytes
from .utils.file import read_file_chunks, read_file
from .utils.json import to_json

if TYPE_CHECKING:
    from .request import Request


class Status(IntEnum):
    """HTTP status codes"""

    def __new__(cls, *args, **kwargs):
        obj = int.__new__(cls, args[0])
        obj._value_ = args[0]
        return obj

    def __init__(self, _: int, description: str = ''):
        self._description_ = description

    @property
    def description(self):
        return self._description_

    CONTINUE = (100, 'Continue')
    SWITCHING_PROTOCOLS = (101, 'Switching Protocols')
    OK = (200, 'OK')
    CREATED = (201, 'Created')
    ACCEPTED = (202, 'Accepted')
    NON_AUTHORITATIVE_INFORMATION = (203, 'Non Authoritative Information')
    NO_CONTENT = (204, 'No Content')
    RESET_CONTENT = (205, 'Reset Content')
    PARTIAL_CONTENT = (206, 'Partial Content')
    MULTIPLE_CHOICES = (300, 'Multiple CHOICES')
    MOVED_PERMANENTLY = (301, 'Moved Permanently')
    FOUND = (302, 'Found')
    SEE_OTHER = (303, 'See Other')
    NOT_MODIFIED = (304, 'Not Modified')
    USE_PROXY = (305, 'Use Proxy')
    TEMPORARY_REDIRECT = (307, 'Temporary Redirect')
    PERMANENTLY_REDIRECT = (308, 'Permanently Redirect')
    BAD_REQUEST = (400, 'Bad Request')
    UNAUTHORIZED = (401, 'Unauthorized')
    PAYMENT_REQUIRED = (402, 'Payment Required')
    FORBIDDEN = (403, 'Forbidden')
    NOT_FOUND = (404, 'Not Found')
    METHOD_NOT_ALLOWED = (405, 'Method Not Allowed')
    NOT_ACCEPTABLE = (406, 'Not Acceptable')
    PROXY_AUTHENTICATION_REQUIRED = (407, 'Proxy Authentication Required')
    REQUEST_TIME_OUT = (408, 'Request Time Out')
    CONFLICT = (409, 'Conflict')
    GONE = (410, 'Gone')
    LENGTH_REQUIRED = (411, 'Length Required')
    PRECONDITION_FAILED = (412, 'Precondition Failed')
    REQUEST_ENTITY_TOO_LARGE = (413, 'Request Entity Too Large')
    REQUEST_URI_TOO_LARGE = (414, 'Request URI Too Large')
    UNSUPPORTED_MEDIA_TYPE = (415, 'Unsupported Media Type')
    REQUESTED_RANGE_NOT_SATISFIABLE = (416, 'Requested Range Not Satisfiable')
    EXPECTATION_FAILED = (417, 'Expectation Failed')
    INTERNAL_SERVER_ERROR = (500, 'Internal Server Error')
    NOT_IMPLEMENTED = (501, 'Not Implemented')
    BAD_GATEWAY = (502, 'Bad Gateway')
    SERVICE_UNAVAILABLE = (503, 'Service Unavailable')
    GATEWAY_TIME_OUT = (504, 'Gateway Time Out')
    HTTP_VERSION_NOT_SUPPORTED = (505, 'HTTP Version Not Supported')


class Response:
    """
    Base HTTP response class whose instances are returned as HTTP responses by requests handlers.

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
        """
        Initialize response instance.

        :param body: The HTTP response body
        :param status: The HTTP response status
        :param headers: The HTTP response headers
        :param content_type: The HTTP response content type
        :param compress: Determines whether or not to compress (gzip) the response
        """
        self.body: Any = body
        self.status: Status = status
        self.headers: Optional[Iterable[[bytes, bytes]]] = headers
        self.content_type: bytes = content_type
        self.compress: bool = compress

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
        stream = self._is_stream(self.body)
        if not stream:
            self.body = to_bytes(self.body)
        self.headers = list(self.headers) if self.headers else []
        if self.compress:
            self.body = self._gzip(self.body) if not stream else self._gzip_stream(self.body)
            self.headers += [[b'content-encoding', b'deflate' if stream else b'gzip']]
        self.headers += [[b'content-type', self.content_type]]
        if not stream:
            self.headers += [[b'content-length', to_bytes(len(self.body))]]
        return self.body, self.status.value, self.headers, stream

    @staticmethod
    def _gzip(body: Any) -> bytes:
        """Gzip the response body"""
        return gzip.compress(body)

    @staticmethod
    async def _gzip_stream(body: Any) -> AsyncGenerator[bytes]:
        """Gzip the response body chunks"""
        c = zlib.compressobj()
        if isinstance(body, types.AsyncGeneratorType):
            async for chunk in body:
                yield c.compress(to_bytes(chunk))
        else:
            for chunk in body:
                yield c.compress(to_bytes(chunk))
        yield c.flush(zlib.Z_FINISH)

    @staticmethod
    def _is_stream(body: Any) -> bool:
        return isinstance(body, types.AsyncGeneratorType) or \
               isinstance(body, types.GeneratorType)


class Text(Response):
    """Text response class inherited from :class:`~backendpy.response.Response` class."""

    def __init__(
            self,
            body: Any,
            status: Status = Status.OK,
            headers: Optional[Iterable[[bytes, bytes]]] = None,
            compress: bool = False) -> None:
        """
        Initialize response instance.

        :param body: The HTTP response body
        :param status: The HTTP response status
        :param headers: The HTTP response headers
        :param compress: Determines whether or not to compress (gzip) the response
        """
        super().__init__(
            body=body,
            status=status,
            headers=headers,
            content_type=b'text/plain',
            compress=compress)


class HTML(Response):
    """HTML response class inherited from :class:`~backendpy.response.Response` class."""

    def __init__(
            self,
            body: Any,
            status: Status = Status.OK,
            headers: Optional[Iterable[[bytes, bytes]]] = None,
            compress: bool = False) -> None:
        """
        Initialize response instance.

        :param body: The HTTP response body
        :param status: The HTTP response status
        :param headers: The HTTP response headers
        :param compress: Determines whether or not to compress (gzip) the response
        """
        super().__init__(
            body=body,
            status=status,
            headers=headers,
            content_type=b'text/html',
            compress=compress)


class JSON(Response):
    """JSON response class inherited from :class:`~backendpy.response.Response` class."""

    def __init__(
            self,
            body: Any,
            status: Status = Status.OK,
            headers: Optional[Iterable[[bytes, bytes]]] = None,
            compress: bool = False) -> None:
        """
        Initialize response instance.

        :param body: The HTTP response body
        :param status: The HTTP response status
        :param headers: The HTTP response headers
        :param compress: Determines whether or not to compress (gzip) the response
        """
        super().__init__(
            body=body,
            status=status,
            headers=headers,
            content_type=b'application/json',
            compress=compress)

    async def __call__(self, request: Request) \
            -> tuple[bytes | AsyncGenerator[bytes],
                     int,
                     list[[bytes, bytes]],
                     bool]:
        self.body = to_json(self.body)
        # TODO: Handle if body is a python generator.
        return await super().__call__(request)


class Binary(Response):
    """Binary object response class inherited from :class:`~backendpy.response.Response` class."""

    def __init__(
            self,
            body: Any,
            status: Status = Status.OK,
            headers: Optional[Iterable[[bytes, bytes]]] = None,
            content_type=b'application/octet-stream',
            compress: bool = False):
        """
        Initialize response instance.

        :param body: The HTTP response body
        :param status: The HTTP response status
        :param headers: The HTTP response headers
        :param content_type: The HTTP response content type
        :param compress: Determines whether or not to compress (gzip) the response
        """
        super().__init__(
            body=body,
            status=status,
            headers=headers,
            content_type=content_type,
            compress=compress)


class File(Response):
    """
    File response class inherited from :class:`~backendpy.response.Response` class
    which reads and returns file from the given path (which should be a path inside
    the project configured media path)
    """

    def __init__(
            self,
            path: str,
            status: Status = Status.OK,
            headers: Optional[Iterable[[bytes, bytes]]] = None,
            stream: bool = True,
            compress: bool = False,
            partial: bool = False,
            last_modified: Optional[int] = None,
            entity_tag: Optional[str] = None):
        """
        Initialize response instance.

        :param path: The file path inside the project media path
        :param status: The HTTP response status
        :param headers: The HTTP response headers
        :param stream: Determines whether or not to stream the response
        :param compress: Determines whether or not to compress (gzip) the response
        :param partial: Determines whether to support partial response
        :param last_modified: Specifies the Last-Modified HTTP header and uses it in the if-range condition check
        :param entity_tag: Specifies the ETag HTTP header and uses it in the if-range condition check
        """
        super().__init__(
            body=b'',
            status=status,
            headers=headers,
            content_type=b'application/octet-stream',
            compress=compress)
        self.path = path
        self.stream = stream
        self.partial = partial
        self.last_modified = last_modified
        self.entity_tag = entity_tag

    async def __call__(self, request: Request) \
            -> tuple[bytes | AsyncGenerator[bytes],
                     int,
                     list[[bytes, bytes]],
                     bool]:
        path = os.path.join(request.app.config['environment']['media_path'], unquote(self.path))
        if not os.path.isfile(path):
            raise FileNotFoundError

        self.headers = list(self.headers) if self.headers else []
        content_type, encoding = guess_type(path)
        self.headers += [[b'content-type', to_bytes(content_type) if content_type else self.content_type],
                         [b'accept-ranges', b'bytes' if self.partial else b'none']]
        try:
            partial = self.partial \
                      and 'range' in request.headers \
                      and request.headers['range'].startswith('bytes=') \
                      and ('if-range' not in request.headers
                           or (self.entity_tag is not None
                               and not self.entity_tag.startswith('/W')
                               and not request.headers['if-range'].startswith('/W')
                               and request.headers['if-range'] == self.entity_tag)
                           or (self.entity_tag is None
                               and self.last_modified is not None
                               and datetime.datetime.utcfromtimestamp(self.last_modified).replace(microsecond=0) ==
                               datetime.datetime.strptime(request.headers['if-range'], '%a, %d %b %Y %H:%M:%S %Z')))
        except ValueError:
            partial = False
        if partial:
            total_length = (await aiofiles.os.stat(path)).st_size
            try:
                ranges = request.headers['range'][6:].split(',')
                range_ = ranges[0].split('-')
                range_start = int(range_[0]) if range_[0] != '' else 0
                range_end = int(range_[1]) if range_[1] != '' else total_length - 1
                is_invalid_range = range_start > range_end or range_end > total_length
            except (ValueError, IndexError):
                is_invalid_range = True
            if is_invalid_range:
                self.status = Status.REQUESTED_RANGE_NOT_SATISFIABLE
                return self.body, self.status.value, self.headers, False
            self.status = Status.PARTIAL_CONTENT
            if self.stream:
                self.body = read_file_chunks(
                    path,
                    chunk_size=int(request.app.config['networking']['stream_size']),
                    start_index=range_start,
                    end_index=range_end)
            else:
                self.body = await read_file(
                    path,
                    start_index=range_start,
                    end_index=range_end)
            self.headers += [[b'content-range', to_bytes(f'bytes {range_start}-{range_end}/{total_length}')],
                             [b'content-length', to_bytes(range_end-range_start+1)]]
        else:
            if self.stream:
                self.body = read_file_chunks(path, int(request.app.config['networking']['stream_size']))
                if self.compress:
                    self.body = self._gzip_stream(self.body)
                    self.headers += [[b'content-encoding', b'deflate']]
                else:
                    file_stat = await aiofiles.os.stat(path)
                    self.headers += [[b'content-length', to_bytes(file_stat.st_size)]]
            else:
                self.body = await read_file(path)
                if self.compress:
                    self.body = self._gzip(self.body)
                    self.headers += [[b'content-encoding', b'gzip']]
                self.headers += [[b'content-length', to_bytes(len(self.body))]]
        if self.last_modified is not None:
            self.headers += [[b'last-modified', to_bytes(self.last_modified)]]
        if self.entity_tag is not None:
            self.headers += [[b'etag', to_bytes(self.entity_tag)]]
        return self.body, self.status.value, self.headers, self.stream


class Redirect(Response):
    """Redirect response class inherited from :class:`~backendpy.response.Response` class."""

    def __init__(
            self,
            url: str | bytes,
            permanent: bool = False,
            method_unchange: bool = True) -> None:
        """
        Initialize response instance.

        :param url: The URL to redirect
        :param permanent: Determines whether the redirect is permanent or not
        :param method_unchange: If true, status codes 307 and 308 will be used, otherwise 301 and 302 will be used
        """
        url = to_bytes(url)
        super().__init__(
            body=url,
            status=(Status.PERMANENTLY_REDIRECT if permanent else Status.TEMPORARY_REDIRECT) if
            method_unchange else (Status.MOVED_PERMANENTLY if permanent else Status.FOUND),
            headers=[[b'location', url],
                     [b'pragma', b'no-cache'],
                     [b'cache-control', b'no-cache']],
            content_type=b'application/octet-stream')


class Success(JSON):
    """JSON formatted success response class inherited from :class:`~backendpy.response.Response` class."""

    def __init__(
            self,
            data: Optional[Any] = None,
            status: Status = Status.OK,
            headers: Optional[Iterable[[bytes, bytes]]] = None,
            compress: bool = False) -> None:
        """
        Initialize response instance.

        :param data: Data with a structure supported by JSON format
        :param status: The HTTP response status
        :param headers: The HTTP response headers
        :param compress: Determines whether or not to compress (gzip) the response
        """
        super().__init__(
            body=None,
            status=status,
            headers=headers,
            compress=compress)
        self.data = data

    async def __call__(self, request: Request) \
            -> tuple[bytes | AsyncGenerator[bytes],
                     int,
                     list[[bytes, bytes]],
                     bool]:
        self.body = {'status': 'success'}
        if self.data is not None:
            self.body['data'] = self.data
        return await super().__call__(request)
