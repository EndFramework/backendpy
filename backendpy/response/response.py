import os
import gzip
import zlib
import types
from mimetypes import guess_type
from urllib.parse import unquote
import aiofiles.os
from ..helpers.bytes import to_bytes
from ..helpers.json import to_json
from ..helpers.file import read_file_chunks, read_file


class Status:
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206
    MULTIPLE_CHOICES = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    TEMPORARY_REDIRECT = 307
    PERMANENTLY_REDIRECT = 308
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIME_OUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    REQUEST_ENTITY_TOO_LARGE = 413
    REQUEST_URI_TOO_LARGE = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    REQUESTED_RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIME_OUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505


class Response:
    def __init__(self, body, status=Status.OK, headers=None, content_type=b'text/plain', compress=False):
        self.body = body
        self.status = status
        self.headers = headers
        self.compress = compress
        self.content_type = content_type

    async def __call__(self, request):
        stream = self._is_stream(self.body)
        if not stream:
            self.body = to_bytes(self.body)
        if not self.headers:
            self.headers = []
        if self.compress:
            self.body = self._gzip(self.body) if not stream else self._gzip_stream(self.body)
            self.headers += [[b'content-encoding', b'deflate' if stream else b'gzip']]
        self.headers += [[b'content-type', self.content_type]]
        if not stream:
            self.headers += [[b'content-length', to_bytes(len(self.body))]]
        return self.body, self.status, self.headers, stream

    @staticmethod
    def _gzip(body):
        return gzip.compress(body)

    @staticmethod
    async def _gzip_stream(body):
        c = zlib.compressobj()
        if isinstance(body, types.AsyncGeneratorType):
            async for chunk in body:
                yield c.compress(to_bytes(chunk))
        else:
            for chunk in body:
                yield c.compress(to_bytes(chunk))
        yield c.flush(zlib.Z_FINISH)

    @staticmethod
    def _is_stream(body):
        return isinstance(body, types.AsyncGeneratorType) or \
               isinstance(body, types.GeneratorType)


class Text(Response):
    def __init__(self, body, status=Status.OK, headers=None, compress=False):
        super().__init__(body=body, status=status, headers=headers, content_type=b'text/plain',
                         compress=compress)


class HTML(Response):
    def __init__(self, body, status=Status.OK, headers=None, compress=False):
        super().__init__(body=body, status=status, headers=headers, content_type=b'text/html',
                         compress=compress)


class JSON(Response):
    def __init__(self, body, status=Status.OK, headers=None, compress=False):
        super().__init__(body=body, status=status, headers=headers, content_type=b'application/json',
                         compress=compress)

    async def __call__(self, *args, **kwargs):
        self.body = to_json(self.body)  # Todo: if body is generator
        return await super().__call__(*args, **kwargs)


class Binary(Response):
    def __init__(self, body, status=Status.OK, headers=None, content_type=b'application/octet-stream',
                 compress=False):
        super().__init__(body=body, status=status, headers=headers, content_type=content_type, compress=compress)


class File(Response):
    def __init__(self, path, status=Status.OK, headers=None, stream=True, compress=False):
        super().__init__(body=b'', status=status, headers=headers, content_type=b'application/octet-stream',
                         compress=compress)
        self.path = path
        self.stream = stream

    async def __call__(self, request):
        self.path = os.path.join(request.app.config['environment']['media_path'], unquote(self.path))
        if not os.path.isfile(self.path):
            raise FileNotFoundError

        if not self.headers:
            self.headers = []
        content_type, encoding = guess_type(self.path)
        self.headers += [[b'content-type', to_bytes(content_type) if content_type else self.content_type]]

        if self.stream:
            self.body = read_file_chunks(self.path, int(request.app.config['networking']['stream_size']))
            if self.compress:
                self.body = self._gzip_stream(self.body)
                self.headers += [[b'content-encoding', b'deflate']]
            else:
                file_stat = await aiofiles.os.stat(self.path)
                self.headers += [[b'content-length', to_bytes(file_stat.st_size)]]
        else:
            self.body = await read_file(self.path)
            if self.compress:
                self.body = self._gzip(self.body)
                self.headers += [[b'content-encoding', b'gzip']]
            self.headers += [[b'content-length', to_bytes(len(self.body))]]

        return self.body, self.status, self.headers, self.stream


class Redirect(Response):
    def __init__(self, url, permanent=False, method_unchange=True):
        url = to_bytes(url)
        super().__init__(body=url,
                         status=(Status.PERMANENTLY_REDIRECT if permanent else Status.TEMPORARY_REDIRECT) if
                         method_unchange else (Status.MOVED_PERMANENTLY if permanent else Status.FOUND),
                         headers=[[b'location', url],
                                  [b'pragma', b'no-cache'],
                                  [b'cache-control', b'no-cache']],
                         content_type=b'application/octet-stream')
