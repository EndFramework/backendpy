from __future__ import annotations

import importlib
import inspect
import os
import sys
from collections.abc import Mapping
from contextvars import ContextVar
from pathlib import Path
from typing import Optional, Any

from .app import App
from .config import get_config
from .error import Error, base_errors
from .exception import ExceptionResponse
from .hook import HookRunner
from .logging import get_logger
from .middleware import MiddlewareProcessor
from .request import Request
from .router import Router
from .templating import Template
from .utils.bytes import to_bytes
from .utils.json import to_json

LOGGER = get_logger(__name__)


class Backendpy:
    """The Backendpy ASGI handler"""

    def __new__(cls, *args, **kwargs):
        """Process Backendpy class instance."""
        config = get_config(project_path=cls._get_project_path())
        cls._add_project_sys_path(config['environment']['project_path'])
        return MiddlewareProcessor(paths=config['middlewares']['active']) \
            .run_process_application(application=super().__new__(cls))

    def __init__(self):
        """Initialize Backendpy class instance."""
        self.config = get_config(project_path=self._get_project_path(), error_logs=True)
        self.context = dict()
        self._request_context_var = ContextVar('request')
        self._hook_runner = HookRunner()
        self._router = Router()
        self._middleware_processor = MiddlewareProcessor(
            paths=self.config['middlewares']['active'])
        self.errors = base_errors
        self._project_apps = self._get_project_apps()
        for app_data in self._project_apps:
            if app_data['app'].routes:
                for i in app_data['app'].routes:
                    self._router.routes.merge(i)
            if app_data['app'].hooks:
                for i in app_data['app'].hooks:
                    self._hook_runner.hooks.merge(i)
            if app_data['app'].errors:
                for i in app_data['app'].errors:
                    self.errors.merge(i)
            if app_data['app'].template_dirs:
                Template.template_dirs[app_data['path']] = \
                    [Path(app_data['path']).joinpath(p) for p in app_data['app'].template_dirs]
        self._lifespan_startup = False

    async def __call__(self, scope, receive, send):
        """Receive the requests and return the responses."""
        if scope['type'] == 'http':
            if not self._lifespan_startup:
                try:
                    await self.execute_event('startup')
                except Exception as e:
                    LOGGER.exception(e)
                else:
                    self._lifespan_startup = True

            try:
                body: bytes = await self._get_request_body(receive)
            except Exception as e:
                LOGGER.exception(f'Request data receive error: {e}')
                await self._send_response(
                    send,
                    to_json(self.errors[1000].as_dict()),
                    self.errors[1000].status.value,
                    [[b'content-type', b'application/json']])
                return

            try:
                request = Request(app=self, scope=scope, body=body)
            except Exception as e:
                LOGGER.exception(f'Request instance creation error: {e}')
                await self._send_response(
                    send,
                    to_json(self.errors[1000].as_dict()),
                    self.errors[1000].status.value,
                    [[b'content-type', b'application/json']])
                return

            if '*' not in self.config['networking']['allowed_hosts'] and \
                    ((not request.headers.get('host') or
                     request.headers['host'] not in self.config['networking']['allowed_hosts']) or
                     (request.headers.get('x-forwarded-host') and
                      request.headers['x-forwarded-host'] not in self.config['networking']['allowed_hosts'])):
                response = Error(1003)
                await self._send_response(send, *await response(request))
                return

            token = self._request_context_var.set(request)
            await self.execute_event('request_start')
            await self._send_response(send, *await self._get_response(request))
            await self.execute_event('request_end')
            self._request_context_var.reset(token)

        elif scope['type'] == 'websocket':
            # TODO
            raise NotImplementedError

        elif scope['type'] == 'lifespan':
            await self._handle_lifespan(receive, send)

    def get_current_request(self):
        """Return the current request object."""
        return self._request_context_var.get()

    def event(self, name: str) -> callable:
        """Register an event hook with python decorator.

        .. seealso:: :func:`~backendpy.hook.Hooks.event`
        """
        return self._hook_runner.hooks.event(name)

    async def execute_event(self, name: str, args: Optional[Mapping[str, Any]] = None) -> None:
        """Trigger all hooks related to the event.

        :param name: The name of an event
        :param args: A dictionary-like object containing arguments passed to the hook function.
        """
        return await self._hook_runner.trigger(name, args)

    async def _handle_lifespan(self, receive, send):
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                try:
                    await self.execute_event('startup')
                except Exception as e:
                    LOGGER.exception(e)
                    await send({'type': 'lifespan.startup.failed',
                                'message': str(e)})
                else:
                    self._lifespan_startup = True
                    await send({'type': 'lifespan.startup.complete'})

            elif message['type'] == 'lifespan.shutdown':
                try:
                    await self.execute_event('shutdown')
                except Exception as e:
                    LOGGER.exception(e)
                    await send({'type': 'lifespan.shutdown.failed',
                                'message': str(e)})
                else:
                    await send({'type': 'lifespan.shutdown.complete'})
                    return

    async def _get_response(self, request):
        try:
            request = await self._middleware_processor.run_process_request(request=request)
        except ExceptionResponse as e:
            return await e(request)
        except Exception as e:
            LOGGER.exception(f'Middleware error: {e}')
            response = Error(1000)
            return await response(request)

        try:
            handler, data_handler_cls, request.url_vars = \
                self._router.match(request.path, request.method, request.scheme)
            if not handler:
                response = Error(1001)
                return await response(request)
        except Exception as e:
            LOGGER.exception(e)
            response = Error(1000)
            return await response(request)

        try:
            handler = await self._middleware_processor.run_process_handler(
                request=request,
                handler=handler)
        except ExceptionResponse as e:
            return await e(request)
        except Exception as e:
            LOGGER.exception(f'Middleware error: {e}')
            response = Error(1000)
            return await response(request)

        try:
            data_errors = None
            if data_handler_cls:
                request.cleaned_data, data_errors = \
                    await data_handler_cls(request=request).get_cleaned_data()
            if data_errors:
                response = Error(1002, data=data_errors)
                return await response(request)
        except Exception as e:
            LOGGER.exception(f'Data handler error: {e}')
            response = Error(1000)
            return await response(request)

        try:
            response = await handler(request=request)
        except ExceptionResponse as e:
            return await e(request)
        except Exception as e:
            LOGGER.exception(f'Handler error: {e}')
            response = Error(1000)
            return await response(request)

        try:
            response = await self._middleware_processor.run_process_response(
                request=request,
                response=response)
        except ExceptionResponse as e:
            return await e(request)
        except Exception as e:
            LOGGER.exception(f'Middleware error: {e}')
            response = Error(1000)
            return await response(request)

        return await response(request)

    @staticmethod
    async def _send_response(send, body, status, headers, stream=False):
        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': headers})

        if stream:
            if hasattr(body, '__aiter__'):
                async for chunk in body:
                    await send({
                        'type': 'http.response.body',
                        'body': to_bytes(chunk),
                        'more_body': True})
            else:
                for chunk in body:
                    await send({
                        'type': 'http.response.body',
                        'body': to_bytes(chunk),
                        'more_body': True})
            await send({
                'type': 'http.response.body',
                'body': b''})
        else:
            await send({
                'type': 'http.response.body',
                'body': to_bytes(body)})

    @staticmethod
    async def _get_request_body(receive) -> bytes:
        # Todo: Problem for a huge body ?
        body = b''
        more_body = True
        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)
        return body

    @staticmethod
    async def _get_request_body_generator(receive):
        more_body = True
        while more_body:
            message = await receive()
            yield message.get('body', b'')
            more_body = message.get('more_body', False)

    def _get_project_apps(self):
        apps: list[dict] = list()
        for package_name in self.config['apps']['active']:
            try:
                module = importlib.import_module(f'{package_name}.main')
                app = getattr(module, 'app')
                if isinstance(app, App):
                    apps.append(dict(
                        package_name=package_name,
                        path=os.path.dirname(os.path.abspath(module.__file__)),
                        app=app))
                else:
                    LOGGER.error(f'"{package_name}" app instance error')
            except (ImportError, AttributeError):
                LOGGER.error(f'"{package_name}" app instance import error')
        return apps

    @staticmethod
    def _get_project_path():
        return os.path.dirname(os.path.realpath(inspect.stack()[2].filename))

    @staticmethod
    def _add_project_sys_path(project_path):
        sys.path.insert(0, os.path.dirname(project_path))
