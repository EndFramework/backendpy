import os
import sys
import importlib
import inspect
from pathlib import Path
from contextvars import ContextVar
from typing import Dict, List, AnyStr, Callable, Any
from configparser import ConfigParser
from .helpers.bytes import to_bytes
from .configuration import get_config, parse_list
from .router import Router, Routes
from .hook import HookRunner, Hooks
from .middleware.processor import MiddlewareProcessor
from .request import Request
from .response.exception import ExceptionResponse
from .response.formatted import Error, ErrorList
from .errors import errors
from .templates import Template
from .logging import logging

LOGGER = logging.getLogger(__name__)


class Backendpy:

    def __new__(cls, *args, **kwargs):
        config = get_config(project_path=cls._get_project_path())
        cls._add_project_sys_path(config['environment']['project_path'])
        return MiddlewareProcessor(paths=parse_list(config['middlewares']['active']))\
            .run_process_application(application=super().__new__(cls))

    def __init__(self):
        self.config = get_config(project_path=self._get_project_path(), error_logs=True)
        self.context = dict()
        self._request_context_var = ContextVar('request')
        self._hook_runner = HookRunner()
        self._router = Router()
        self._middleware_processor = MiddlewareProcessor(
            paths=parse_list(self.config['middlewares']['active']))
        self.errors = errors
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
        if scope['type'] == 'http':
            if not self._lifespan_startup:
                try:
                    await self.execute_event('startup')
                except Exception as e:
                    LOGGER.exception(e)
                else:
                    self._lifespan_startup = True

            try:
                request = self._get_request()
            except Exception as e:
                response = Error(1000, e)
                await self._send_response(send, *await response(None))
                return

            try:
                await self._receive_request_data(request, scope, receive)
            except Error as e:
                await self._send_response(send, *await e(request))
                return

            token = self._request_context_var.set(request)
            await self.execute_event('request_start')
            await self._send_response(send, *await self._get_response(request))
            await self.execute_event('request_end')
            self._request_context_var.reset(token)

        elif scope['type'] == 'websocket':
            # Todo
            raise NotImplementedError

        elif scope['type'] == 'lifespan':
            await self._handle_lifespan(receive, send)

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

    def _get_request(self):
        return Request(app=self)

    async def _receive_request_data(self, request, scope, receive):
        try:
            request.apply_scope(scope)
            request.apply_body(await self._get_request_body(receive))
        except Exception as e:
            LOGGER.exception(e)
            raise Error(1001, e)

    async def _get_response(self, request):
        try:
            request = await self._middleware_processor.run_process_request(request=request)
        except ExceptionResponse as e:
            return await e(request)
        except Exception as e:
            LOGGER.exception(e)
            response = Error(1002, e)
            return await response(request)

        try:
            handler, data_handler_cls, request.url_vars = \
                self._router.match(request.path, request.method, request.scheme)
            if not handler:
                response = Error(1005)
                return await response(request)
        except Exception as e:
            LOGGER.exception(e)
            response = Error(1000, e)
            return await response(request)

        try:
            handler = await self._middleware_processor.run_process_handler(
                    request=request,
                    handler=handler)
        except ExceptionResponse as e:
            return await e(request)
        except Exception as e:
            LOGGER.exception(e)
            response = Error(1002, e)
            return await response(request)

        try:
            data_errors = None
            if data_handler_cls:
                request.cleaned_data, data_errors = \
                    await data_handler_cls(request=request).get_cleaned_data()
            if data_errors:
                response = Error(1006, data=data_errors)
                return await response(request)
        except Exception as e:
            LOGGER.exception(e)
            response = Error(1004, e)
            return await response(request)

        try:
            response = await handler(request=request)
        except ExceptionResponse as e:
            return await e(request)
        except Exception as e:
            LOGGER.exception(e)
            response = Error(1003, e)
            return await response(request)

        try:
            response = await self._middleware_processor.run_process_response(
                    request=request,
                    response=response)
        except ExceptionResponse as e:
            return await e(request)
        except Exception as e:
            LOGGER.exception(e)
            response = Error(1002, e)
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
    async def _get_request_body(receive):
        # Todo: Security problem for huge body ?
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

    def get_current_request(self):
        return self._request_context_var.get()

    def uri(self, *args, **kwargs):
        return self._router.routes.uri(*args, **kwargs)

    def event(self, *args, **kwargs):
        return self._hook_runner.hooks.event(*args, **kwargs)

    async def execute_event(self, *args, **kwargs):
        return await self._hook_runner.execute(*args, **kwargs)

    def _get_project_apps(self):
        apps: List[Dict] = list()
        for package_name in parse_list(self.config['apps']['active']):
            try:
                module = importlib.import_module(f'{package_name}.main')
                app = getattr(module, 'app')
                if isinstance(app, App):
                    apps.append(dict(
                        package_name=package_name,
                        path=os.path.dirname(os.path.abspath(module.__file__)),
                        app=app))
                else:
                    LOGGER.error(f'app "{package_name}" instance error')
            except (ImportError, AttributeError):
                LOGGER.error(f'app "{package_name}" instance import error')
        return apps

    @staticmethod
    def _get_project_path():
        return os.path.dirname(os.path.realpath(inspect.stack()[2].filename))

    @staticmethod
    def _add_project_sys_path(project_path):
        sys.path.insert(0, os.path.dirname(project_path))


class App:
    def __init__(self,
                 routes: List[Routes],
                 hooks: List[Hooks] = None,
                 models: List[AnyStr] = None,
                 template_dirs: List[AnyStr] = None,
                 errors: List[ErrorList] = None,
                 init_func: Callable[[ConfigParser], Any] = None):
        self.routes = routes
        self.hooks = hooks
        self.models = models
        self.template_dirs = template_dirs
        self.errors = errors
        self.init_func = init_func
