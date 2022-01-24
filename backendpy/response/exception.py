from ..helpers.json import to_json
from .response import Status, Response


class ExceptionResponse(BaseException, Response):
    def __init__(self, body, status=Status.OK, headers=None, content_type=b'text/plain', compress=False):
        BaseException.__init__(self)
        Response.__init__(self, body=body, status=status, headers=headers, content_type=content_type, compress=compress)

    async def __call__(self, *args, **kwargs):
        return await super().__call__(*args, **kwargs)


class BadRequest(ExceptionResponse):
    def __init__(self, body=b'Bad Request', content_type=None):
        super().__init__(body=body if type(body) is not dict else to_json(body),
                         status=Status.BAD_REQUEST,
                         content_type=content_type if content_type else
                         (b'text/plain' if type(body) is not dict else b'application/json'))


class Unauthorized(ExceptionResponse):
    def __init__(self, body=b'Unauthorized', content_type=None):
        super().__init__(body=body if type(body) is not dict else to_json(body),
                         status=Status.UNAUTHORIZED,
                         content_type=content_type if content_type else
                         (b'text/plain' if type(body) is not dict else b'application/json'))


class Forbidden(ExceptionResponse):
    def __init__(self, body=b'Forbidden', content_type=None):
        super().__init__(body=body if type(body) is not dict else to_json(body),
                         status=Status.FORBIDDEN,
                         content_type=content_type if content_type else
                         (b'text/plain' if type(body) is not dict else b'application/json'))


class NotFound(ExceptionResponse):
    def __init__(self, body=b'Not Found', content_type=None):
        super().__init__(body=body if type(body) is not dict else to_json(body),
                         status=Status.NOT_FOUND,
                         content_type=content_type if content_type else
                         (b'text/plain' if type(body) is not dict else b'application/json'))


class ServerError(ExceptionResponse):
    def __init__(self, body=b'Internal Server Error', content_type=None):
        super().__init__(body=body if type(body) is not dict else to_json(body),
                         status=Status.INTERNAL_SERVER_ERROR,
                         content_type=content_type if content_type else
                         (b'text/plain' if type(body) is not dict else b'application/json'))
