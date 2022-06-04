from __future__ import annotations

import inspect
import os
from collections.abc import Mapping, Iterable
from typing import Optional, Any

import aiofiles

from .utils.bytes import to_bytes

try:
    import jinja2
except ImportError:
    pass


class Template:
    """A class for reading and rendering templates (requires jinja2 package to be installed)."""

    template_dirs = dict()

    def __init__(
            self,
            path: Optional[str | bytes] = None,
            source: Optional[str] = None):
        """
        Initialize template instance.

        :param path: The name or path of the template file inside the application templates dir
        :param source: Source code of the template (This parameter is used when the template file
                       path is not specified and we want to use source code instead of file)
        """
        if path:
            self._path = path
            self._source = None
        elif source:
            self._source = source
        else:
            raise ValueError('Template path or source is not specified')
        self._template = None

    def _get_caller_app_template_dirs(self) -> list[str]:
        call_path = inspect.stack()[2].filename
        for app_path, app_template_dirs in self.template_dirs.items():
            if call_path.startswith(app_path):
                return app_template_dirs
        else:
            raise FileNotFoundError('Template dir not found')

    @staticmethod
    async def _read_template(
            template_paths: Iterable[str],
            path: str | bytes) -> str:
        for template_path in template_paths:
            try:
                async with aiofiles.open(os.path.join(to_bytes(template_path), to_bytes(path)), mode='r') as template:
                    return str(await template.read())
            except FileNotFoundError:
                pass
        else:
            raise FileNotFoundError('Template file not found')

    async def render(
            self,
            context: Optional[Mapping[str, Any]] = None,
            **kwargs) -> str:
        """
        Render the context inside the template.

        :param context: Context values (in the structure of a mapping) that the template
                        variables will take
        :param kwargs: Context values (taken as a keyword arguments) that the template
                       variables will take
        :return: Rendered template in string format
        """
        _context = kwargs
        if context and isinstance(context, Mapping):
            _context.update(context)

        if self._template is None:
            if self._source is None:
                self._source = await self._read_template(self._get_caller_app_template_dirs(), self._path)
            self._template = jinja2.Template(source=self._source, enable_async=True)

        return await self._template.render_async(_context)
