import inspect
from copy import deepcopy
from .fields import Field
from .fields import TYPE_JSON, TYPE_FORM, TYPE_PARAMS, TYPE_URL_VARS, TYPE_FILES, TYPE_HEADER


class Data:
    def __init__(self, request, default=None):
        self._request = request
        self._fields = {i[0]: deepcopy(i[1]) for i in inspect.getmembers(self) if isinstance(i[1], Field)}
        self._default_data = default if type(default) is dict else \
            (default.__dict__ if hasattr(default, "__dict__") else {})
        self._raw_data = {
            TYPE_JSON: request.json if request.json is not None else {},
            TYPE_FORM: request.form if request.form is not None else {},
            TYPE_PARAMS: request.params if request.params is not None else {},
            TYPE_URL_VARS: request.url_vars if request.url_vars is not None else {},
            TYPE_FILES: request.files if request.files is not None else {},
            TYPE_HEADER: request.headers}

    async def get_cleaned_data(self):
        data = dict()
        cleaned_data = dict()
        errors = dict()
        for name, field in self._fields.items():
            k = field.data_name if field.data_name else name
            if k in self._raw_data[field.type]:
                data[name] = self._raw_data[field.type][k]
            elif name in self._default_data:
                data[name] = self._default_data[name]
        for name, field in self._fields.items():
            if name in data:
                await field.set_value(
                    value=data[name],
                    meta={'name': name,
                          'received_data': data,
                          'request': self._request})
                if field.errors:
                    errors[name] = field.errors
                cleaned_data[name] = field.value if (field.value != '' and field.value != b'') else None
            elif field.required:
                errors[name] = 'Required'
        return cleaned_data, errors
