from __future__ import annotations

import asyncio
import base64
import concurrent.futures.thread
import datetime
import decimal
from collections.abc import Iterable, Sequence
from functools import partial
from html import escape, unescape
from io import BytesIO
from typing import Any, Optional

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

    async def __call__(self, value: str):
        if value in (None, '', b''):
            return value
        if type(value) is not str:
            raise TypeError('Escape filter only supports string type.')
        return escape(unescape(value), quote=True)


class Cut(Filter):
    """Cut the sequence to desired length."""

    def __init__(self, length: int):
        self.length = length

    async def __call__(self, value: Sequence):
        if value in (None, '', b''):
            return value
        return value[:self.length]


class DecodeBase64(Filter):
    """Decode the Base64 encoded bytes-like object or ASCII string."""

    async def __call__(self, value: bytes | str):
        if value in (None, '', b''):
            return value
        return base64.b64decode(value, validate=True)


class ParseDateTime(Filter):
    """Convert datetime string to datetime object."""

    def __init__(self, format: str = '%Y-%m-%d %H:%M:%S'):
        self.format = format

    async def __call__(self, value: str):
        if value in (None, '', b''):
            return value
        return datetime.datetime.strptime(value, self.format)


class ToIntegerObject(Filter):
    """Convert value to integer object."""

    async def __call__(self, value):
        if value in (None, '', b''):
            return value
        try:
            return int(value)
        except ValueError:
            if type(value) is str and '.' in value:
                return int(value.split('.')[0])
        raise ValueError('The input value cannot be converted to int type')


class ToFloatObject(Filter):
    """Convert value to float object."""

    async def __call__(self, value):
        if value in (None, '', b''):
            return value
        return float(value)


class ToDecimalObject(Filter):
    """Convert value to decimal object."""

    async def __call__(self, value) -> decimal.Decimal:
        if value in (None, '', b''):
            return value
        return decimal.Decimal(str(value))


class ToBooleanObject(Filter):
    """Convert input values 0, 1, '0', '1', 'true' and 'false' to boolean value."""

    async def __call__(self, value) -> bool:
        if value in (None, '', b''):
            return value
        if value in (True, 1, 'true', '1'):
            return True
        elif value in (False, 0, 'false', '0'):
            return False
        raise ValueError("Only input values 0, 1, '0', '1', 'true' and 'false' are acceptable.")


class BlankToNull(Filter):
    """Convert blank value to null value."""

    async def __call__(self, value):
        if value in ('', b''):
            return None
        return value


class ModifyImage(Filter):
    """Modify the image."""

    def __init__(self, format: str = 'JPEG', mode: str = 'RGB',
                 max_size: Optional[Iterable[float, float]] = None):
        self.format = format
        self.mode = mode
        self.max_size = max_size

    async def __call__(self, value: bytes) -> bytes:
        if value in (None, '', b''):
            return value
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await asyncio.get_running_loop().run_in_executor(
                pool, partial(self._modify, value))

    def _modify(self, value: bytes) -> bytes:
        # Todo: (read from / write to) buffer ?
        with BytesIO(value) as f_in:
            im = Image.open(f_in)
            if im.mode != self.mode:
                im = im.convert(self.mode)
            if self.max_size is not None:
                thumb_im = im.thumbnail(self.max_size, Image.ANTIALIAS)
                if thumb_im is not None:
                    im = thumb_im
            with BytesIO() as f_out:
                im.save(f_out, format=self.format)
                return f_out.getvalue()
