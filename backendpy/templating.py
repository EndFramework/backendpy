import os
import inspect
import aiofiles
try:
    import jinja2
except ImportError:
    pass


class Template:

    template_dirs = dict()

    def __init__(self, path=None, source=None):
        if path:
            self.path = path
            self.source = None
        elif source:
            self.source = source
        else:
            raise ValueError('Template path/source is not specified')
        self.template = None

    def _get_template_dirs(self):
        call_path = inspect.stack()[2].filename
        for app_path, template_dirs in self.template_dirs.items():
            if call_path.startswith(app_path):
                return template_dirs
        else:
            raise FileNotFoundError('Template dir not found')

    @staticmethod
    async def _read_template(template_paths, path):
        for template_path in template_paths:
            try:
                async with aiofiles.open(os.path.join(template_path, path), mode='r') as template:
                    return await template.read()
            except FileNotFoundError:
                pass
        else:
            raise FileNotFoundError('Template file not found')

    async def render(self, context, **kwargs):
        _context = kwargs
        if type(context) is dict:
            _context.update(context)

        if self.template is None:
            if self.source is None:
                self.source = await self._read_template(self._get_template_dirs(), self.path)
            self.template = jinja2.Template(source=self.source, enable_async=True)

        return await self.template.render_async(_context)
