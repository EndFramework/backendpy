from __future__ import annotations

import cgi
import datetime
import re
import sys
import uuid
from collections.abc import Mapping, Sequence
from typing import Any, Optional
from urllib.parse import urlparse

from ..utils.file import get_human_readable_size, get_extension, get_type

try:
    from sqlalchemy import select, exists
except ImportError:
    pass


class Validator:
    """
    The base class that will be inherited to create the data validator classes.

    :ivar message: Error message that this validator will return if it receives invalid data
    """

    def __init__(self, message: str):
        """
        Initialize data validator instance.

        :param message: Error message that this validator will return if it receives invalid data
        """
        self.message = message

    async def __call__(
            self,
            value: Any,
            meta: Mapping[str, Any]) -> None | str:
        """
        Perform data validation operations.

        :param value: Data to be validated
        :param meta: Information beyond the value of this field that may be required
                     during the validation process; Such as information of other received data
                     fields, request information, etc.
        :return: If there is no error or discrepancy in the data, the ``None`` will be
                 returned, otherwise the error message will be returned
        """
        return None


class NotNull(Validator):
    """
    Check that the value is not null.
    (Note: NotNull validator is different from the ``required`` parameter of the
    :class:`~backendpy.data_handler.fields.Field` and has a separate purpose.
    Because sometimes we need to differentiate between not sending a value to
    a field and sending a null value to it.)
    """

    def __init__(self, message: str = 'Null value'):
        super().__init__(message)

    async def __call__(self, value, meta):
        return None if value not in (None, '', b'') else self.message


class In(Validator):
    """Check if the value is present among the predefined values."""

    def __init__(
            self,
            values: Sequence,
            message: str = 'Value error'):
        super().__init__(message)
        self.values = values

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        if value not in self.values:
            return self.message
        return None


class NotIn(Validator):
    """Check if the value is not present among the predefined values."""

    def __init__(
            self,
            values: Sequence,
            message: str = 'Value error'):
        super().__init__(message)
        self.values = values

    async def __call__(self, value, meta):
        if value in self.values:
            return self.message
        return None


class Length(Validator):
    """Check data string length."""

    def __init__(
            self,
            equal: Optional[int] = None,
            min: Optional[int] = None,
            max: Optional[int] = None,
            message: str = 'Length error'):
        super().__init__(message)
        self.equal = equal
        self.min = min
        self.max = max
        if self.equal is not None:
            self.message += ' acceptable: %s' % self.equal
        else:
            if self.min is not None:
                self.message += ' min: %s' % self.min
            if self.max is not None:
                self.message += ' max: %s' % self.max

    async def __call__(self, value, meta):
        if value is None:
            return None
        value = str(value)
        if self.equal is not None and len(value) != self.equal:
            return self.message
        else:
            if self.max is not None and len(value) > self.max:
                return self.message
            elif self.min is not None and len(value) < self.min:
                return self.message
        return None


class Limit(Validator):
    """Used for numerical data and checks whether the number is in the range of min and max."""

    def __init__(
            self,
            min: Optional[float] = None,
            max: Optional[float] = None,
            message: str = 'Value limit error'):
        super().__init__(message)
        self.min = min
        self.max = max
        if self.min is not None:
            self.message += ' min: %s' % self.min
        if self.max is not None:
            self.message += ' max: %s' % self.max
            
    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        try:
            value = float(value)
        except:
            try:
                value = int(value)
            except:
                return self.message
        if self.max is not None and value > self.max:
            return self.message
        elif self.min is not None and value < self.min:
            return self.message
        return None


class UUID(Validator):
    """Check that the submitted data has a valid UUID4 format."""

    def __init__(self, message: str = 'Invalid UUID'):
        super().__init__(message)

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        try:
            uuid_obj = uuid.UUID(value, version=4)
            if str(uuid_obj) == value:
                return None
        except:
            pass
        return self.message


class EmailAddress(Validator):
    """Check if the data is a valid email address."""

    def __init__(self, message: str = 'Invalid email address'):
        super().__init__(message)

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        if len(value) > 7 and \
                re.match(r'^[-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*'
                         r'(\.[-a-z0-9_]+)*\.([a-z][a-z]+)|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
                         r'))(:[0-9]{1,5})?$', value):
            return None
        return self.message


class Numeric(Validator):
    """Check if the data is a numeric value."""

    def __init__(self, message: str = 'Must be numeric'):
        super().__init__(message)

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        try:
            int(value)
        except:
            try:
                float(value)
            except:
                return self.message
        return None


class Boolean(Validator):
    """Check if the data is a boolean value."""

    def __init__(self, message: str = 'Must be boolean'):
        super().__init__(message)

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        if value in (True, False, 'true', 'false'):
            return None
        return self.message


class Url(Validator):
    """Check if the data is a valid URL."""

    def __init__(self, message: str = 'Invalid URL'):
        super().__init__(message)

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        try:
            result = urlparse(value)
            if result.scheme and result.netloc:
                return None
        except:
            pass
        return self.message


class UrlPath(Validator):
    """Check if the data is a valid URL path."""

    def __init__(self, message: str = 'Invalid Path'):
        super().__init__(message)

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        if re.match(r'^/(([^/]*)((/[^/]+)*))$', value):
            return None
        return self.message


class PasswordStrength(Validator):
    """Checks the hardness of a password and returns an error if the password is weak."""

    def __init__(self, message: str = 'Weak password'):
        super().__init__(message)

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        if len(value) < 10:
            return self.message
        else:
            score = 50
            num = {'excess': 0, 'uppers': 0, 'numbers': 0, 'symbols': 0}
            bonus = {'excess': 3, 'uppers': 4, 'numbers': 5, 'symbols': 5, 'combo': 0, 'all_lower': 0,
                     'all_number': 0, 'regulated': 0, 'repeated': 0}
            num['excess'] = len(value) - 8
            num['upperss'] = len(re.findall(r'[A-Z]', value))
            num['numbers'] = len(re.findall(r'[0-9]', value))
            num['symbols'] = len(re.findall(r'[!,@,#,$,%,^,&,*,?,_,~]', value))
            if num['uppers'] and num['numbers'] and num['symbols']:
                bonus['combo'] = 25
            elif (num['uppers'] and num['numbers']) or (num['uppers'] and num['symbols']) or \
                    (num['numbers'] and num['symbols']):
                bonus['combo'] = 15
            if re.match(r'^[\sa-z]+$', value):
                bonus['all_lower'] = -30
            elif re.match(r'^[\s0-9]+$', value):
                bonus['all_number'] = -90
            if value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz012345678909876543210' \
                        'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm':
                bonus['regulated'] = -35
            else:
                for i in range(len(value)-1):
                    if value[i] == value[i+1]:
                        if re.match(r'^[\sa-z]$', value[i]):
                            bonus['repeated'] -= 3;
                        elif re.match(r'^[A-Z]$', value[i]):
                            bonus['repeated'] -= 7;
                        elif re.match(r'^[0-9]|[!,@,#,$,%,^,&,*,?,_,~]$', value[i]):
                            bonus['repeated'] -= 8;
            score = score + (num['excess'] * bonus['excess']) + (num['uppers'] * bonus['uppers']) + \
                    (num['numbers'] * bonus['numbers']) + (num['symbols'] * bonus['symbols']) + \
                    bonus['combo'] + bonus['all_lower'] + bonus['all_number'] + bonus['regulated'] + bonus['repeated']
            if score < 50:
                return self.message
            else:
                return None


class Date(Validator):
    """Verifies that the value is in the valid format of YYYY-MM-DD date."""

    def __init__(self, message: str = 'Invalid date format (YYYY-MM-DD)'):
        super().__init__(message)

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            return self.message
        return None


class MatchRegex(Validator):
    """Checks that the value matches a regular expression pattern."""

    def __init__(self, pattern: str, message: str = 'Invalid format'):
        super().__init__(message)
        self.pattern = pattern
        
    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        if not self.pattern:
            return None
        if re.match(self.pattern, value):
            return None
        else:
            return self.message


class RestrictedFile(Validator):
    """
    Used for file fields and validates file type and size according to predefined
    valid extensions and size range.
    """

    def __init__(
            self,
            extensions: Optional[Sequence[str]] = None,
            max_size: Optional[float] = None,
            min_size: Optional[float] = None,
            message: str = 'File error'):
        """
        Initialize file validator instance.

        :param extensions: List of allowed file extensions
        :param max_size: Maximum file size in bytes
        :param min_size: Minimum file size in bytes
        :param message: Error message that will be returned if the file is invalid
        """
        super().__init__(message)
        self.extensions = extensions if extensions else tuple()
        self.max_size = (float(max_size) * 1024.0) if max_size is not None else None
        self.min_size = (float(min_size) * 1024.0) if min_size is not None else None

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        f = value
        filename = None
        if isinstance(f, cgi.FieldStorage):
            if f.file:
                filename = f.filename
                if self.max_size is not None:
                    try:
                        value = f.value[:int(self.max_size)+1]
                    except IndexError:
                        value = f.value
                else:
                    value = f.value
            else:
                return self.message
        elif isinstance(f, bytes):
            value = f
        else:
            return self.message
        # check value
        if value:
            # check size
            size = sys.getsizeof(value)
            if self.max_size is not None and size > self.max_size:
                return '%s: %s %s' % (self.message, 'max size:', str(get_human_readable_size(self.max_size)))
            elif self.min_size is not None and size < self.min_size:
                return '%s: %s %s' % (self.message, 'min size', str(get_human_readable_size(self.min_size)))
            # check extension
            if self.extensions:
                if filename and get_extension(filename) not in self.extensions:
                    return '%s: %s' % (self.message, 'Invalid file type')
                # check content
                detected_types = get_type(value)
                if detected_types:
                    for typ in detected_types:
                        if typ in self.extensions:
                            break
                    else:
                        return '%s: %s' % (self.message, 'Invalid file type')
                else:
                    return '%s: %s' % (self.message, 'Invalid file type')
            # filters passed
            return None
        return self.message


class Unique(Validator):
    """
    This validator is used to check the uniqueness of the data in the database table and can
    be used when using the default database helpers of the framework.
    """

    def __init__(
            self,
            model: object,
            model_field_name: Optional[str] = None,
            except_self: Optional[str] = None,
            except_default: bool = False,
            case_sensitive: bool = False,
            message: str = 'Unique value error'):
        """
        Initialize validator instance.

        :param model: Object of database model to check for uniqueness
        :param model_field_name: The name of the database table field that must be checked for uniqueness.
                                 This parameter only needs to be set if the name of the database table field
                                 to be checked is different from the name of the data handler class field.
        :param except_self: The name of identifier field of database table (This ID field value must also be set
                            in input data). We only need to set this parameter when we are editing a row from
                            the database table (not adding a new row) and we do not want to return the non-unique
                            value error if the previous value of the unique field for this row is retrieved.
        :param except_default: Specifies whether to return a non-unique value error if the value is equal to
                               the default value defined for data handler class field.
        :param message: Error message that will be returned if the value is not unique
        """
        super().__init__(message)
        self.model = model
        self.model_field_name = model_field_name
        self.except_self = except_self
        self.except_default = except_default
        self.case_sensitive = case_sensitive

    async def __call__(self, value, meta):
        # Todo: Support for case sensitive uniqueness check
        if value in (None, '', b''):
            return None
        if not self.model:
            return self.message
        model_field = getattr(self.model, self.model_field_name if self.model_field_name else meta['name'])
        if self.except_default is True and meta.get('default') is not None and meta['default'] == value:
            return None
        if self.except_self is not None and \
                meta['received_data'].get(self.except_self) is not None:
            model_except_field = getattr(self.model, self.except_self)
            q = select(exists()
                       .where(model_field == value)
                       .where(model_except_field != meta['received_data'][self.except_self]))
            result = await meta['request'].app.context['db_session']().execute(q)
            if not result.scalar():
                return None
        else:
            q = select(exists()
                       .where(model_field == value))
            result = await meta['request'].app.context['db_session']().execute(q)
            if not result.scalar():
                return None
        return self.message


'''class List(Validator):
    
    def __init__(self, inner_processors=None, message: str = 'Must be list'):
        super().__init__(message)
        self.inner_processors = inner_processors

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        if type(value) is list:
            if not self.inner_processors:
                return None
            for p in self.inner_processors:
                for v in value:
                    if isinstance(p, Validator):
                        err = await p(v, meta)
                        if err is not None:
                            return err
                    elif isinstance(p, Filter) and v is not None:
                        v = await p(v)  # Todo
            else:
                return None
        return self.message
'''