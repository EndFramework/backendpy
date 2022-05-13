from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Optional, Any, Union

from .filters import Filter
from .validators import Validator

TYPE_JSON = 1
TYPE_FORM = 2
TYPE_PARAMS = 3
TYPE_URL_VARS = 4
TYPE_FILES = 5
TYPE_HEADER = 6


class Field:
    """
    Basic class for defining a data field.

    :ivar data_name: The name of the received data field
                     (Note: The name of the received data field can be defined differently
                     from the name of the Python field inside the data handler class)
    :ivar type: It is possible to get different fields from different locations in a
                request. For example, take one field from the URL and another field from
                the form, where all of these values are passed to the handler in a single format.
                The type can take the following values which are available from
                the :class:`~backendpy.data_handler.fields` module: ``TYPE_JSON``, ``TYPE_FORM``,
                ``TYPE_PARAMS``, ``TYPE_URL_VARS``, ``TYPE_FILES``, ``TYPE_HEADER``
    :ivar value: Field value
    :ivar required: Specifies whether the field is required or optional
    :ivar errors: List of error messages related to the data in this field
    """

    def __init__(
            self,
            name: Optional[str] = None,
            default: Optional[Any] = None,
            processors: Optional[Iterable[Union[Validator, Filter]] |
                                 Iterable[Iterable[Union[Validator, Filter]]]] = None,
            field_type=TYPE_JSON,
            required: bool = False):
        """
        Initialize data field instance.

        :param name: The name of the received data field
                    (Note: The name of the received data field can be defined differently
                    from the name of the Python field inside the data handler class)
        :param default: Default value for this field when no data is sent to it
        :param processors: A combined iterable of :class:`~backendpy.data_handler.validators.Validator`s
                           and :class:`~backendpy.data_handler.filters.Filter`s in the desired order
                           that will be applied to the data in this field.
                           (Note: If the received data is itself a list of different values and the
                           processors need to be applied to its internal values instead of applying
                           to the whole data, the processors must be defined inside another
                           iterable (as a Nested iterables) at the time of definition.)
        :param field_type: It is possible to get different fields from different locations in a
                           Request. For example, take one field from the URL and another field from
                           the form, where all of these values are passed to the Handler in a single format.
                           The field_type parameter can take the following values which are available from
                           the :class:`~backendpy.data_handler.fields` module: ``TYPE_JSON``, ``TYPE_FORM``,
                           ``TYPE_PARAMS``, ``TYPE_URL_VARS``, ``TYPE_FILES``, ``TYPE_HEADER``
        :param required: Specifies whether the field is required or optional
        """
        self.data_name = name
        self.type = field_type
        self.value = default
        self.required = required
        self._processors = processors if processors else None
        self.errors = []

    async def set_value(
            self,
            value: Any,
            meta: Mapping[str, Any]) -> None:
        """After applying the processors to the value, set the value to the field."""
        if value is None and self.value is not None:
            return
        if self._processors:
            self.value = await self._apply_processors(self._processors, value, meta)
        else:
            self.value = value

    async def _apply_processors(
            self,
            processors: Iterable[Union[Validator, Filter]] | Iterable[Iterable[Union[Validator, Filter]]],
            value: Any,
            meta: Mapping[str, Any]):
        """Apply the processors to the field data."""
        if processors:
            for p in processors:
                if isinstance(p, Validator):
                    err = await p(value, meta)
                    if err is not None:
                        self.errors.append(err)
                        return None
                elif isinstance(p, Filter) and value is not None:
                    value = await p(value)
                elif isinstance(p, Iterable):
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
    """String data field class"""
    # Todo: set type annotations and default validators
    pass
