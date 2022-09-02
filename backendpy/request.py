from __future__ import annotations

from collections.abc import Mapping
from email.parser import BytesParser
from typing import TYPE_CHECKING, Optional, Any
from urllib.parse import parse_qs

from .utils.json import from_json

if TYPE_CHECKING:
    from .asgi import Backendpy


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
    :ivar form: A dictionary of HTTP request form data
    :ivar json: A dictionary of HTTP request JSON data
    :ivar files: A dictionary of multipart HTTP request files data
    :ivar body: Raw body of HTTP request if it does not belong to any of the "form",
                "json" and "file" fields
    :ivar cleaned_data: A dictionary of data processed by request data handler
    """

    def __init__(
            self,
            app: Backendpy,
            scope: Mapping[str, Any],
            body: Optional[bytes] = None,
            url_vars: Optional[dict[str, str]] = None) -> None:
        """
        Initialize request instance.

        :param app: :class:`~backendpy.Backendpy` class instance of the current
                    project (that is an ASGI application)
        :param scope: HTTP connection scope
        :param body: Body of HTTP request
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
        self.form: Optional[dict[str, str | list[str]]] = None
        self.json: Optional[dict[str, Any]] = None
        self.files: Optional[dict[str, dict]] = None
        self.body: Optional[bytes] = None
        self.cleaned_data: Optional[dict[str, Any]] = None
        self._apply_scope(scope)
        if body:
            self._apply_body(body)

    def _apply_scope(self, scope: Mapping[str, Any]) -> None:
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
            self.params = {k: (v[0] if len(v) == 1 else v)
                           for k, v in parse_qs(scope['query_string'].decode('utf8')).items()}

    def _apply_body(self, body: bytes) -> None:
        """Set request body."""
        if self.headers is None:
            raise Exception('Request information is not applied.')
        if self.headers.get('content-type') == 'application/json':
            self.json = from_json(body)
        elif self.headers.get('content-type') == 'application/x-www-form-urlencoded':
            self.form = {k: (v[0] if len(v) == 1 else v)
                         for k, v in parse_qs(body.decode('utf8')).items()}
        elif self.headers.get('content-type') == 'multipart/form-data':
            json_parts = dict()
            form_parts = dict()
            file_parts = dict()
            text_parts = dict()
            for part in BytesParser().parsebytes(body).get_payload():
                part_type = part.get_content_type()
                if part_type == 'application/json':
                    json_parts[part.get_param(param='name', header='content-disposition')] = \
                        from_json(part.get_payload())
                elif part_type == 'application/x-www-form-urlencoded':
                    form_parts[part.get_param(param='name', header='content-disposition')] = \
                        {k: (v[0] if len(v) == 1 else v)
                         for k, v in parse_qs(part.get_payload().decode('utf8')).items()}
                elif part_type == 'application/octet-stream':
                    file_parts[part.get_param(param='name', header='content-disposition')] = \
                        {'content': part.get_payload(),
                         'file-name': part.get_param(param='filename', header='content-disposition'),
                         'content-type': part.get_content_subtype()}  # Todo: test
                elif part_type == 'text/plain':
                    text_parts[part.get_param(param='name', header='content-disposition')] = \
                        str(part.get_payload(decode=True))
            if json_parts:
                self.json = json_parts if len(json_parts) > 1 else json_parts[0]
            if form_parts:
                self.form = form_parts if len(form_parts) > 1 else form_parts[0]
            if file_parts:
                self.files = file_parts
            if text_parts:
                self.body = text_parts if len(text_parts) > 1 else text_parts[0]
        else:
            self.body = body
