from .validators import Validator
from .filters import Filter

TYPE_JSON = 1
TYPE_FORM = 2
TYPE_PARAMS = 3
TYPE_URL_VARS = 4
TYPE_FILES = 5
TYPE_HEADER = 6


class Field:
    def __init__(self, name=None, default=None, processors=None, field_type=TYPE_JSON, required=False):
        self.data_name = name
        self.type = field_type
        self.value = default
        self.required = required
        self._processors = processors if processors else None
        self.errors = []

    async def set_value(self, value, meta):
        if value is None and self.value is not None:
            return
        self.value = await self._apply_processors(self._processors, value, meta)

    async def _apply_processors(self, processors, value, meta):
        if processors:
            for p in processors:
                if isinstance(p, Validator):
                    err = await p(value, meta)
                    if err is not None:
                        self.errors.append(err)
                        return None
                elif isinstance(p, Filter) and value is not None:
                    value = await p(value)
                elif type(p) is list:
                    if type(value) is list:
                        for i, v in enumerate(value):
                            value[i] = await self._apply_processors(p, v, meta)
                            if self.errors:
                                return None
                    elif value not in (None, '', b''):
                        self.errors.append('Required list data')
                        return None
        return value


class String(Field):
    pass
