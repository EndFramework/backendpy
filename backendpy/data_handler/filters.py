from __future__ import annotations

import asyncio
import base64
import concurrent.futures.thread
from functools import partial
from html import escape, unescape
from io import BytesIO
from typing import Any

try:
    from PIL import Image
except ImportError:
    pass


class Filter:
    """The base class that will be inherited to create the data filter classes."""

    async def __call__(self, value: Any) -> Any:
        """
        Perform data filtering operation.

        :param value: The data to which the filter should be applied
        :return: Filtered value
        """
        return value


class Escape(Filter):
    """Replace special characters "&", "<", ">", (') and (") to HTML-safe sequences."""

    async def __call__(self, value: str) -> str:
        if type(value) is not str:
            raise TypeError('Escape filter only supports string type.')
        return escape(unescape(value), quote=True)


class Cut(Filter):
    """Cut the sequence to desired length."""

    def __init__(self, length: int):
        self.length = length

    async def __call__(self, value):
        return value[:self.length]


class DecodeBase64(Filter):
    """Decode the Base64 encoded bytes-like object or ASCII string."""

    async def __call__(self, value: bytes | str) -> bytes:
        return base64.b64decode(value, validate=True)


class ModifyImage(Filter):
    """Change the image format."""

    def __init__(self, format: str = 'JPEG', mode: str = 'RGB'):
        self.format = format
        self.mode = mode

    async def __call__(self, value: bytes) -> bytes:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await asyncio.get_running_loop().run_in_executor(
                pool, partial(self._modify, value))

    def _modify(self, value: bytes) -> bytes:
        # Todo: (read from / write to) buffer ?
        with BytesIO(value) as f_in:
            im = Image.open(f_in)
            if im.mode != self.mode:
                im = im.convert(self.mode)
            with BytesIO() as f_out:
                im.save(f_out, format=self.format)
                return f_out.getvalue()


"""
class ModifyVideo(Filter):
    def __init__(self, format='MP4'):
        self.format = format

    async def __call__(self, value):
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await asyncio.get_running_loop().run_in_executor(
                pool, partial(self._modify, value))

    def _modify(self, value):
        # Todo
        return value


class ModifyAudio(Filter):
    def __init__(self, format='MP3'):
        self.format = format

    async def __call__(self, value):
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await asyncio.get_running_loop().run_in_executor(
                pool, partial(self._modify, value))

    def _modify(self, value):
        # Todo
        return value
"""
