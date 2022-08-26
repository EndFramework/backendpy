from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Optional

from .error import ErrorList
from .hook import Hooks
from .router import Routes


class App:
    """
    A class used to define Backendpy internal application.

    :ivar routes: Iterable of instances of the Routes class
    :ivar hooks: Iterable of instances of the Hooks class (or None)
    :ivar models: Iterable of module paths that contain database models (or None)
    :ivar template_dirs: Iterable of paths (within the application directory)
                         from which templates will be searched (or None)
    :ivar errors: Iterable of instances of the ErrorList class (or None)
    :ivar init_func: The initialization function of the application (or None)
    """

    def __init__(
            self,
            routes: Iterable[Routes],
            hooks: Optional[Iterable[Hooks]] = None,
            models: Optional[Iterable[str]] = None,
            template_dirs: Optional[Iterable[str]] = None,
            errors: Optional[Iterable[ErrorList]] = None,
            init_func: Optional[callable[[Mapping], Any]] = None):
        """
        Initialize application instance

        :param routes: Iterable of instances of the Routes class
        :param hooks: Iterable of instances of the Hooks class (or None)
        :param models: Iterable of module paths that contain database models (or None)
        :param template_dirs: Iterable of paths (within the application directory)
                              from which templates will be searched (or None)
        :param errors: Iterable of instances of the ErrorList class (or None)
        :param init_func: The initialization function of the application (or None)
        """
        self.routes = routes
        self.hooks = hooks
        self.models = models
        self.template_dirs = template_dirs
        self.errors = errors
        self.init_func = init_func
