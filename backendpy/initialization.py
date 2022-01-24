import os
import sys
import importlib
from inspect import iscoroutinefunction
from .app import App
from .configuration import get_config, parse_list
from .logging import logging

LOGGER = logging.getLogger(__name__)


class Init:
    def __init__(self, project_path):
        self.config = get_config(project_path)
        sys.path.append(os.path.dirname(self.config["environment"]["project_path"]))

    async def __call__(self):
        try:
            for package_name in parse_list(self.config['apps']['active']):
                try:
                    app = getattr(importlib.import_module(f'{package_name}.main'), 'app')
                    if isinstance(app, App):
                        if app.init_func:
                            if iscoroutinefunction(app.init_func):
                                await app.init_func(self.config)
                            else:
                                LOGGER.error(f'app "{package_name}" init error: '
                                             f'init_func() must be a coroutine function')
                    else:
                        LOGGER.error(f'app "{package_name}" init error: '
                                     f'app instance error')
                except (ImportError, AttributeError):
                    LOGGER.error(f'app "{package_name}" init error: '
                                 f'app instance import error')
        except Exception as e:
            LOGGER.error(f'Failed to run initializations: {e}')
