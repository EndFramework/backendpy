import asyncio
import base64
import concurrent.futures.thread
from html import escape, unescape
from io import BytesIO
from functools import partial
try:
    from PIL import Image
except ImportError:
    pass


class Filter:
    async def __call__(self, value):
        return value


class Escape(Filter):
    async def __call__(self, value):
        if type(value) in (str, bytes):
            value = escape(unescape(value), quote=True)
        return value


class Cut(Filter):
    def __init__(self, length):
        self.length = length

    async def __call__(self, value):
        return value[:self.length]


class DecodeBase64(Filter):
    async def __call__(self, value):
        return base64.b64decode(value)


class ModifyImage(Filter):
    def __init__(self, format='JPEG', mode='RGB'):
        self.format = format
        self.mode = mode

    async def __call__(self, value):
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await asyncio.get_running_loop().run_in_executor(
                pool, partial(self._modify, value))

    def _modify(self, value):
        # Todo: (read from / write to) buffer ?
        with BytesIO(value) as f_in:
            im = Image.open(f_in)
            if im.mode != self.mode:
                im = im.convert(self.mode)
            with BytesIO() as f_out:
                im.save(f_out, format=self.format)
                return f_out.getvalue()


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
