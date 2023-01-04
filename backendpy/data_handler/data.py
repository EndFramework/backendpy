from __future__ import annotations

import inspect
from collections.abc import Mapping
from copy import deepcopy
from typing import Optional, Any

from .fields import Field
from .fields import TYPE_JSON_FIELD, TYPE_FORM_FIELD, TYPE_PARAM, TYPE_URL_VAR, TYPE_FILE, TYPE_CONTENT, TYPE_HEADER
from ..request import Request


class Data:
    """The base class that will be inherited to create data handler classes."""

    def __init__(self, default: Optional[Mapping[str, Any]] = None):
        """
        Initialize data handler instance.

        :param request: :class:`~backendpy.request.Request` class instance
        :param default: Optional default values for the data handler fields
        """
        self._fields = {i[0]: deepcopy(i[1]) for i in inspect.getmembers(self) if isinstance(i[1], Field)}
        self._default_data = default if type(default) is dict else \
            (default.__dict__ if hasattr(default, "__dict__") else {})
        self.auto_blank_to_null = True

    async def get_cleaned_data(self, request: Request) \
            -> tuple[dict[str, Optional[Any]],
                     dict[str, str | list[str]]]:
        """Return the processed data of the data handler class and related error messages."""
        data = dict()
        cleaned_data = dict()
        errors = dict()
        for name, field in self._fields.items():
            k = field.data_name if field.data_name else name
            if field.type == TYPE_JSON_FIELD \
                    and request.body.json is not None \
                    and k in request.body.json:
                data[name] = request.body.json[k]
            elif field.type == TYPE_FORM_FIELD \
                    and request.body.form is not None \
                    and k in request.body.form:
                data[name] = request.body.form[k]
            elif field.type == TYPE_PARAM \
                    and request.params is not None \
                    and k in request.params:
                data[name] = request.params[k]
            elif field.type == TYPE_URL_VAR \
                    and request.url_vars is not None \
                    and k in request.url_vars:
                data[name] = request.url_vars[k]
            elif field.type == TYPE_FILE \
                    and request.body.files is not None \
                    and k in request.body.files:
                data[name] = request.body.files[k]['content']
            elif field.type == TYPE_CONTENT \
                    and request.body.content is not None:
                data[name] = request.body.content
            elif field.type == TYPE_HEADER \
                    and k in request.headers:
                data[name] = request.headers[k]
            elif name in self._default_data:
                data[name] = self._default_data[name]
        for name, field in self._fields.items():
            if name in data:
                await field.set_value(
                    value=data[name] if ((data[name] != '' and data[name] != b'')
                                         or not self.auto_blank_to_null) else None,
                    meta={'name': name,
                          'received_data': data,
                          'request': request})
                if field.errors:
                    errors[name] = field.errors
                cleaned_data[name] = field.value
            elif field.required:
                errors[name] = 'Required'
        return cleaned_data, errors
