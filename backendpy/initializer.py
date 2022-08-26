import importlib
import os
import sys
from inspect import iscoroutinefunction

from .app import App
from .config import get_config
from .logging import get_logger

LOGGER = get_logger(__name__)


class Init:
    def __init__(self, project_path):
        self.config = get_config(project_path)
        sys.path.append(os.path.dirname(self.config["environment"]["project_path"]))

    async def __call__(self):
        try:
            for package_name in self.config['apps']['active']:
                try:
                    app = getattr(importlib.import_module(f'{package_name}.main'), 'app')
                    if isinstance(app, App):
                        if app.init_func:
                            if iscoroutinefunction(app.init_func):
                                await app.init_func(self.config)
                            else:
                                LOGGER.error(f'"{package_name}" init error: '
                                             f'The init_func must be a coroutine function')
                    else:
                        LOGGER.error(f'"{package_name}" init error: '
                                     f'App instance error')
                except (ImportError, AttributeError):
                    LOGGER.error(f'"{package_name}" init error: '
                                 f'App instance import error')
        except Exception as e:
            LOGGER.error(f'Failed to run initializations: {e}')
