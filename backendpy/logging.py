from __future__ import annotations
import logging as _logging
from typing import Optional

NOTSET = _logging.NOTSET
DEBUG = _logging.DEBUG
INFO = _logging.INFO
WARNING = _logging.WARNING
ERROR = _logging.ERROR
CRITICAL = _logging.CRITICAL


class Logger(_logging.Logger):
    """Subclass of :class:`logging.Logger` that produces colored logs."""

    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    ORANGE = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

    def debug(self, msg, *args, **kwargs):
        super().debug(f"{self.BLUE}{msg}{self.ENDC}", *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        super().info(f"{self.GREEN}{msg}{self.ENDC}", *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        super().warning(f"{self.ORANGE}{msg}{self.ENDC}", *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        super().error(f"{self.RED}{msg}{self.ENDC}", *args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        super().exception(f"{self.RED}{msg}{self.ENDC}", *args, exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, **kwargs):
        super().critical(f"{self.RED}{msg}{self.ENDC}", *args, **kwargs)


def get_logger(
        name: str,
        level: Optional[int | str] = None) -> Logger:
    """
    Return a logger using :class:`backendpy.logging.Logger` class.

    :param name: Logger name
    :param level: Logging level
    """
    _logging.setLoggerClass(Logger)
    _logging.basicConfig(level=level if level is not None else DEBUG)
    return _logging.getLogger(name)
