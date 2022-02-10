from .response import Status, JSON
from .exception import ExceptionResponse


class Error(ExceptionResponse, JSON):
    def __init__(self, code, message_data=None, data=None, headers=None, compress=False):
        JSON.__init__(self, body=None, status=None, headers=headers, compress=compress)
        self.code = code
        self.data = data
        self.message_data = message_data

    async def __call__(self, request):
        error = request.app.errors[self.code]

        self.status = error.status
        self.body = {
            'status': 'error',
            'code': self.code}

        if self.message_data:
            if type(self.message_data) is dict:
                self.body['message'] = error.message.format(**self.message_data)
            elif type(self.message_data) is tuple:
                self.body['message'] = error.message.format(*self.message_data)
            else:
                self.body['message'] = error.message.format(self.message_data)
        else:
            self.body['message'] = error.message

        if self.data is not None:
            self.body['data'] = self.data
        return await JSON.__call__(self, request)


class ErrorCode:
    def __init__(self, code, message, status):
        self._code = code
        self._message = message
        self._status = status

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    @property
    def status(self):
        return self._status


class ErrorList:
    def __init__(self, *codes):
        self._items = dict()
        self.extend(*codes)

    @property
    def items(self):
        return self._items

    def extend(self, *codes):
        for i in codes:
            if not isinstance(i, ErrorCode):
                raise Exception(f'invalid error code defined')
            if i.code in self._items:
                raise Exception(f'duplicate error code "{i.code}" defined')
            self._items[i.code] = i

    def merge(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'can not merge the "ErrorList" and "{type(other)}"')
        for code, i in other.items.items():
            if code in self._items:
                raise Exception(f'duplicate error code "{code}" defined')
            self._items[code] = i

    def __getitem__(self, item):
        return self._items[item]


base_errors = ErrorList(
    ErrorCode(1000, "Server error", Status.INTERNAL_SERVER_ERROR),
    ErrorCode(1001, "Not found", Status.NOT_FOUND),
    ErrorCode(1002, "Unexpected data", Status.BAD_REQUEST),)
