import os
import sys
import argparse
import asyncio
from backendpy.configuration import get_config
from backendpy.logging import logging
from backendpy.initialization import Init
try:
    from backendpy.db import create_database
except ImportError:
    pass


LOGGER = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(prog='backendpy', allow_abbrev=False)
    sub_parser = parser.add_subparsers(dest='command')

    create_project = sub_parser.add_parser('create_project')
    create_project.add_argument('-n', '--name', type=str, required=True)
    create_project.add_argument('-f', '--full', action='store_true', default=False)

    sub_parser.add_parser('init_project')

    create_app = sub_parser.add_parser('create_app')
    create_app.add_argument('-n', '--name', type=str, required=True)
    create_app.add_argument('-f', '--full', action='store_true', default=False)

    sub_parser.add_parser('create_db')

    args = parser.parse_args()

    if args.command == 'create_db':
        config = get_config(os.getcwd())
        sys.path.append(os.path.dirname(config["environment"]["project_path"]))
        create_database(app_config=config)

    elif args.command == 'create_project':
        current_dir = os.getcwd()
        project_name = args.name

        project_path = os.path.join(current_dir, project_name)
        project_module_path = os.path.join(project_path, project_name)

        if args.full:
            paths = (
                (project_path, 0o755),
                (os.path.join(project_path, 'media'), 0o755),
                (os.path.join(project_path, 'media', 'dev'), 0o755),
                (project_module_path, 0o755),
                (os.path.join(project_module_path, 'apps'), 0o755),
                (os.path.join(project_module_path, 'apps', 'hello'), 0o755),
                (os.path.join(project_module_path, 'apps', 'hello', 'controllers'), 0o755),
                (os.path.join(project_module_path, 'apps', 'hello', 'middlewares'), 0o755),
                (os.path.join(project_module_path, 'apps', 'hello', 'db'), 0o755),
                (os.path.join(project_module_path, 'apps', 'hello', 'templates'), 0o755))
            files = (
                (os.path.join(project_module_path, '__init__.py'), 0o644, ''),
                (os.path.join(project_module_path, 'config.ini'), 0o600,
                    f'''; Backendpy Configurations

[networking]
stream_size = 32768

[environment]
media_path = {os.path.join(project_path, 'media')}

[apps]
active =
    {project_name}.apps.hello
;   backendpy_accounts

[middlewares]
active =
    {project_name}.apps.hello.middlewares.example.Example
;   backendpy_accounts.middleware.auth.AuthMiddleware

;[database]
;host = localhost
;port = 5432
;name = {project_name}
;username = 
;password = 

'''),
                (os.path.join(project_module_path, 'config.dev.ini'), 0o600,
                    f'''; Backendpy Configurations

[networking]
stream_size = 32768

[environment]
media_path = {os.path.join(project_path, 'media', 'dev')}

[apps]
active =
    {project_name}.apps.hello
;   backendpy_accounts

[middlewares]
active =
    {project_name}.apps.hello.middlewares.example.Example
;   backendpy_accounts.middleware.auth.AuthMiddleware

;[database]
;host = localhost
;port = 5432
;name = {project_name}_dev
;username = 
;password = 

'''),
                (os.path.join(project_module_path, 'asgi.py'), 0o644,
                    '''from backendpy.app import Backendpy
# from backendpy.db import set_database_hooks

app = Backendpy()
# Uncomment this line to activate default database sessions
# set_database_hooks(app)

'''),
                (os.path.join(project_module_path, 'backendpy.sh'), 0o744,
                    '''# Uncomment this line to use dev environment
# export BACKENDPY_ENV = dev
uvicorn asgi:app --host '127.0.0.1' --port 8000

'''),
                (os.path.join(project_module_path, 'apps', '__init__.py'), 0o644, ''),
                (os.path.join(project_module_path, 'apps', 'hello', '__init__.py'), 0o644, ''),
                (os.path.join(project_module_path, 'apps', 'hello', 'main.py'), 0o644,
                    f'''from backendpy.app import App
from .controllers import api, views
from .controllers.hooks import hooks
from .controllers.errors import errors

app = App(
    routes=[api.routes, views.routes],
    hooks=[hooks],
    errors=[errors],
    # models=['{project_name}.apps.hello.db.models'],
    template_dirs=['templates'])

'''),
                (os.path.join(project_module_path, 'apps', 'hello', 'controllers', '__init__.py'), 0o644, ''),
                (os.path.join(project_module_path, 'apps', 'hello', 'controllers', 'api.py'), 0o644,
                    '''from backendpy.router import Routes
from backendpy.response.formatted import Success, Error

routes = Routes()


@routes.uri(r'^/hello-world$', ['GET'])
async def hello(request):
    return Success('Hello World!')


@routes.uri(r'^/example-error$', ['GET'])
async def example_error(request):
    raise Error(2001)

'''),
                (os.path.join(project_module_path, 'apps', 'hello', 'controllers', 'views.py'), 0o644,
                    '''from backendpy.router import Routes
from backendpy.response.response import HTML
from backendpy.templates import Template

routes = Routes()


@routes.uri(r'^/home$', ['GET'])
async def home(request):
    context = {'message': 'Hello World!'}
    return HTML(await Template('home.html').render(context))

'''),
                (os.path.join(project_module_path, 'apps', 'hello', 'controllers', 'hooks.py'), 0o644,
                    '''from backendpy.hook import Hooks
from backendpy.logging import logging

LOGGER = logging.getLogger(__name__)

hooks = Hooks()


@hooks.event('startup')
async def example():
    LOGGER.debug("Example event executed!")

'''),
                (os.path.join(project_module_path, 'apps', 'hello', 'controllers', 'errors.py'), 0o644,
                    '''from backendpy.response.formatted import ErrorList, ErrorCode
from backendpy.response.response import Status

errors = ErrorList(
    ErrorCode(2000, "Example server error!", Status.INTERNAL_SERVER_ERROR),
    ErrorCode(2001, "Example bad request error!", Status.BAD_REQUEST),
)

'''),
                (os.path.join(project_module_path, 'apps', 'hello', 'middlewares', '__init__.py'), 0o644, ''),
                (os.path.join(project_module_path, 'apps', 'hello', 'middlewares', 'example.py'), 0o644,
                    '''from backendpy.middleware.middleware import Middleware
from backendpy.logging import logging

LOGGER = logging.getLogger(__name__)


class Example(Middleware):

    @staticmethod
    async def process_request(request):
        LOGGER.debug("Example request middleware executed!")
        return request

'''),      
                (os.path.join(project_module_path, 'apps', 'hello', 'db', '__init__.py'), 0o644, ''),
                (os.path.join(project_module_path, 'apps', 'hello', 'db', 'models.py'), 0o644,
                    '''
'''),
                (os.path.join(project_module_path, 'apps', 'hello', 'db', 'queries.py'), 0o644,
                    '''
'''),
                (os.path.join(project_module_path, 'apps', 'hello', 'templates', 'home.html'), 0o644,
                    '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Backendpy</title>
</head>
<body>
  <h1>{{ message }}</h1>
</body>
</html>

'''),
                (os.path.join(project_path, '.gitignore'), 0o644,
                    '''__pycache__/
*.py[cod]
*$py.class

config*.ini
media/*
'''),
            )

        else:
            paths = (
                (project_path, 0o755),
                (project_module_path, 0o755),
                (os.path.join(project_module_path, 'apps'), 0o755),
                (os.path.join(project_module_path, 'apps', 'hello'), 0o755),
                (os.path.join(project_module_path, 'apps', 'hello', 'controllers'), 0o755))
            files = (
                (os.path.join(project_module_path, '__init__.py'), 0o644, ''),
                (os.path.join(project_module_path, 'config.ini'), 0o600,
                    f'''; Backendpy Configurations

[apps]
active =
    {project_name}.apps.hello

'''
                 ),
                (os.path.join(project_module_path, 'asgi.py'), 0o644,
                    '''from backendpy.app import Backendpy

app = Backendpy()

'''),
                (os.path.join(project_module_path, 'backendpy.sh'), 0o744,
                    '''# Uncomment this line to use dev environment
# export BACKENDPY_ENV = dev
uvicorn asgi:app --host '127.0.0.1' --port 8000
                 
'''),
                (os.path.join(project_module_path, 'apps', '__init__.py'), 0o644, ''),
                (os.path.join(project_module_path, 'apps', 'hello', '__init__.py'), 0o644, ''),
                (os.path.join(project_module_path, 'apps', 'hello', 'main.py'), 0o644,
                    '''from backendpy.app import App
from .controllers.api import routes


app = App(
    routes=[routes])

'''),
                (os.path.join(project_module_path, 'apps', 'hello', 'controllers', '__init__.py'), 0o644, ''),
                (os.path.join(project_module_path, 'apps', 'hello', 'controllers', 'api.py'), 0o644,
                    '''from backendpy.router import Routes
from backendpy.response import response

routes = Routes()


@routes.uri(r'^/hello-world$', ['GET'])
async def hello(request):
    return response.Text('Hello World!')

'''),
                (os.path.join(project_path, '.gitignore'), 0o644,
                    '''__pycache__/
*.py[cod]
*$py.class

config*.ini
media/*
'''),
            )
        try:
            for path, mode in paths:
                os.mkdir(path, mode=mode)
            for path, mode, data in files:
                with os.fdopen(os.open(path, flags=os.O_WRONLY | os.O_CREAT, mode=mode), 'wt') as file:
                    file.write(data)
        except Exception as e:
            LOGGER.error(f"Project creation error: {e}")
            exit()
        finally:
            LOGGER.info(f"Backendpy project created successfully!")

    elif args.command == 'init_project':
        init = Init(project_path=os.getcwd())
        asyncio.get_event_loop().run_until_complete(init())

    elif args.command == 'create_app':
        current_dir = os.getcwd()
        app_name = args.name

        app_path = os.path.join(current_dir, app_name)

        if args.full:
            paths = (
                (app_path, 0o755),
                (os.path.join(app_path, 'controllers'), 0o755),
                (os.path.join(app_path, 'middlewares'), 0o755),
                (os.path.join(app_path, 'db'), 0o755),
                (os.path.join(app_path, 'templates'), 0o755))
            files = (
                (os.path.join(app_path, '__init__.py'), 0o644, ''),
                (os.path.join(app_path, 'main.py'), 0o644,
                    f'''from backendpy.app import App
from .controllers import api, views
from .controllers.hooks import hooks
from .controllers.errors import errors

app = App(
    routes=[api.routes, views.routes],
    hooks=[hooks],
    errors=[errors],
    # models=['<APP PYTHON PATH.>{app_name}.db.models'],
    template_dirs=['templates'])

'''),
                (os.path.join(app_path, 'controllers', '__init__.py'), 0o644, ''),
                (os.path.join(app_path, 'controllers', 'api.py'), 0o644,
                    '''from backendpy.router import Routes
from backendpy.response.formatted import Success, Error

routes = Routes()


@routes.uri(r'^/hello-world$', ['GET'])
async def hello(request):
    return Success('Hello World!')


@routes.uri(r'^/example-error$', ['GET'])
async def example_error(request):
    raise Error(2001)

'''),
                (os.path.join(app_path, 'controllers', 'views.py'), 0o644,
                    '''from backendpy.router import Routes
from backendpy.response.response import HTML
from backendpy.templates import Template

routes = Routes()


@routes.uri(r'^/home$', ['GET'])
async def home(request):
    context = {'message': 'Hello World!'}
    return HTML(await Template('home.html').render(context))

'''),
                (os.path.join(app_path, 'controllers', 'hooks.py'), 0o644,
                    '''from backendpy.hook import Hooks
from backendpy.logging import logging

LOGGER = logging.getLogger(__name__)

hooks = Hooks()


@hooks.event('startup')
async def hello():
    LOGGER.debug("Example event executed!")

'''),
                (os.path.join(app_path, 'controllers', 'errors.py'), 0o644,
                    '''from backendpy.response.formatted import ErrorList, ErrorCode
from backendpy.response.response import Status

errors = ErrorList(
    ErrorCode(2000, "Example server error!", Status.INTERNAL_SERVER_ERROR),
    ErrorCode(2001, "Example bad request error!", Status.BAD_REQUEST),
)

'''),
                (os.path.join(app_path, 'middlewares', '__init__.py'), 0o644, ''),
                (os.path.join(app_path, 'middlewares', 'example.py'), 0o644,
                    '''from backendpy.middleware.middleware import Middleware
from backendpy.logging import logging

LOGGER = logging.getLogger(__name__)


class Example(Middleware):
                 
    @staticmethod
    async def process_request(request):
        LOGGER.debug("Example request middleware executed!")
        return request

'''),
                (os.path.join(app_path, 'db', '__init__.py'), 0o644, ''),
                (os.path.join(app_path, 'db', 'models.py'), 0o644,
                    '''
'''
                 ),
                (os.path.join(app_path, 'db', 'queries.py'), 0o644,
                    '''
'''
                 ),
                (os.path.join(app_path, 'templates', 'home.html'), 0o644,
                    '''<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Backendpy</title>
    </head>
    <body>
        <h1>{{ message }}</h1>
    </body>
</html>

'''),
            )

        else:
            paths = (
                (app_path, 0o755),
                (os.path.join(app_path, 'controllers'), 0o755))
            files = (
                (os.path.join(app_path, '__init__.py'), 0o644, ''),
                (os.path.join(app_path, 'main.py'), 0o644,
                    '''from backendpy.app import App
from .controllers.api import routes


app = App(
    routes=[routes])

'''),
                (os.path.join(app_path, 'controllers', '__init__.py'), 0o644, ''),
                (os.path.join(app_path, 'controllers', 'api.py'), 0o644,
                    '''from backendpy.router import Routes
from backendpy.response import response

routes = Routes()


@routes.uri(r'^/hello-world$', ['GET'])
async def hello(request):
    return response.Text('Hello World!')

'''),
            )

        try:
            for path, mode in paths:
                os.mkdir(path, mode=mode)
            for path, mode, data in files:
                with os.fdopen(os.open(path, flags=os.O_WRONLY | os.O_CREAT, mode=mode), 'wt') as file:
                    file.write(data)
        except Exception as e:
            LOGGER.error(f"App creation error: {e}")
            exit()
        finally:
            LOGGER.info(f"Backendpy app created successfully!")
