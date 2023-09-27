from __future__ import annotations

from collections.abc import Mapping, AsyncIterable, Callable, Awaitable
from email import parser
from typing import TYPE_CHECKING, Optional, Any, Type
from urllib.parse import parse_qs

from .error import Error
from .logging import get_logger
from .utils.json import from_json

if TYPE_CHECKING:
    from .asgi import Backendpy
    from .data_handler.data import Data

LOGGER = get_logger(__name__)


class Request:
    """
    Base HTTP request class whose instances are used to store the information of a request
    and then these instances are sent to the requests handlers.

    :ivar app: :class:`~backendpy.Backendpy` class instance of the current project (that is an ASGI application).
               The information that is defined in the general scope of the project can be accessed through the
               app field of each request. For example ``request.app.config`` contains project config information.
               Also, if we want to put information in the App context, this information can be saved or read from
               ``request.app.context``. The data stored in the App context is valid until the service is stopped.
               For example, you can put a database connection in it to be used in the scope of all requests and until
               the service is turned off.
    :ivar context: A dictionary of request context variables. Applications and middlewares can store their
                   own data in the request context for other components to use until the end of the request.
                   For example, auth middleware can set a user's information into request context after
                   authentication process in the start of the request, so that other sections in the path of
                   handling the request, can use the authenticated user information for their operations.
                   The scope of the data stored in the request context is the request itself and until it responds.
    :ivar method: Method of HTTP request
    :ivar path: URL path of HTTP request
    :ivar root_path: The root path this ASGI application is mounted at
    :ivar scheme: URL scheme of HTTP request
    :ivar server: A dictionary of server information (including host and port)
    :ivar client: A dictionary of client information (including remote host and port)
    :ivar headers: A dictionary of HTTP request headers
    :ivar url_vars: A dictionary of URL path variables
    :ivar params: A dictionary of HTTP request query string values
    :ivar body: A :class:`~backendpy.request.RequestBody` class instance
    """

    def __init__(
            self,
            app: Backendpy,
            scope: Mapping[str, Any],
            body_receiver: Optional[Callable[..., Awaitable[dict]]] = None,
            url_vars: Optional[dict[str, str]] = None) -> None:
        """
        Initialize request instance.

        :param app: :class:`~backendpy.Backendpy` class instance of the current
                    project (that is an ASGI application)
        :param scope: HTTP connection scope
        :param body_receiver: Async callable to receive request body chunks
        :param url_vars: URL path variables of HTTP request
        """
        self.app: Backendpy = app
        self.context: dict[str, Any] = {}
        self.method: Optional[str] = None
        self.path: Optional[str] = None
        self.root_path: Optional[str] = None
        self.scheme: Optional[str] = None
        self.server: Optional[dict[str, Any]] = None
        self.client: Optional[dict[str, Any]] = None
        self.headers: Optional[dict[str, str]] = None
        self.url_vars: Optional[dict[str, str]] = url_vars
        self.params: Optional[dict[str, str | list[str]]] = None
        self._data_handler: Optional[Type[Data]] = None
        self._set_scope_data(scope)
        self.body: RequestBody = RequestBody(content_type=self.headers.get('content-type'),
                                             receiver=body_receiver)

    def _set_scope_data(self, scope: Mapping[str, Any]) -> None:
        """Set request information from HTTP connection scope."""
        if scope.get('server'):
            self.server = {'host': scope['server'][0],
                           'port': scope['server'][1]}
        if scope.get('client'):
            self.client = {'ip': scope['client'][0],
                           'port': scope['client'][1]}
        self.method = scope['method']
        self.path = scope['path']
        self.root_path = scope['root_path']
        self.scheme = scope['scheme']
        self.headers = {k.decode(): v.decode() for k, v in scope['headers']}
        if scope.get('query_string'):
            self.params = {k: (v[-1] if not k.endswith('[]') else v)
                           for k, v in parse_qs(scope['query_string'].decode('utf8')).items()}

    async def get_cleaned_data(self) -> Optional[dict[str, Any]]:
        """Return a dictionary of data processed by request data handler"""
        await self.body()
        if self._data_handler:
            try:
                cleaned_data, data_errors = \
                    await self._data_handler().get_cleaned_data(request=self)
                if data_errors:
                    raise Error(1002, data=data_errors)
                return cleaned_data
            except Exception as e:
                LOGGER.exception(f'Data handle error: {e}')
                raise Error(1000)
        else:
            return None


class RequestBody:
    """
    HTTP request body class whose instances are used to store the information of a request
    and then these instances are sent to the requests handlers.

    :ivar form: A dictionary of HTTP request form data
    :ivar json: A dictionary of HTTP request JSON data
    :ivar files: A dictionary of multipart HTTP request files data
    :ivar text: HTTP request text body or a dictionary of text parts
    :ivar bytes: Raw body of HTTP request if it does not belong to any of the "form",
                "json", "file" and "text" fields
    """
    def __init__(self,
                 body: bytes = None,
                 content_type: str = None,
                 receiver: Optional[Callable[..., Awaitable[dict]]] = None) -> None:
        self.form: Optional[dict[str, str | list[str]]] = None
        self.json: Optional[dict[str, Any]] = None
        self.files: Optional[dict[str, dict]] = None
        self.content: Optional[bytes | str | dict[str, str | bytes] | list[str | bytes]] = None
        self._receiver: Optional[Callable[..., Awaitable[dict]]] = receiver
        self._is_received = False
        self._content_type = content_type
        if body is not None:
            self.set_received_body(body)

    async def __call__(self):
        if not self._is_received:
            self.set_received_body(await self.receive())
        return self

    async def receive(self) -> bytes:
        """Receive request body"""
        if self._is_received:
            raise Exception('The request body has already been received')
        else:
            self._is_received = True
        body = b''
        async for chunk in self.receive_stream():
            body += chunk
        return body

    async def receive_stream(self) -> AsyncIterable[bytes]:
        """Stream request body"""
        self._is_received = True
        try:
            more_body = True
            while more_body:
                message = await self._receiver()
                yield message.get('body', b'')
                more_body = message.get('more_body', False)
        except Exception as e:
            LOGGER.exception(f'Request data receive error: {e}')
            raise Error(1000)

    def set_received_body(self, body: bytes) -> None:
        """Parse and set the received request body"""
        if body:
            if self._content_type == 'application/json':
                self.json = from_json(body)
            elif self._content_type == 'application/x-www-form-urlencoded':
                self.form = {k: (v[0] if len(v) == 1 else v)
                             for k, v in parse_qs(body.decode('utf8')).items()}
            elif self._content_type and self._content_type.startswith('multipart/form-data'):
                self.form = dict()
                self.files = dict()
                body = str.encode(f'content-type: {self._content_type}\n') + body
                for part in parser.BytesParser().parsebytes(body).get_payload():
                    if part.get_param(param='filename', header='content-disposition'):
                        self.files[part.get_param(param='name', header='content-disposition')] = \
                            {'content': part.get_payload(decode=True),
                             'file-name': part.get_param(param='filename', header='content-disposition'),
                             'content-type': part.get_content_type()
                             if part.get_content_type() else 'application/octet-stream'}
                    else:
                        self.form[part.get_param(param='name', header='content-disposition')] = \
                            str(part.get_payload(decode=True))
            elif self._content_type == 'text/plain':
                self.content = str(body)
            else:
                self.content = body
