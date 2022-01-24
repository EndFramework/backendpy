import sys
import cgi
import re
import datetime
import uuid
from urllib.parse import urlparse
from ..helpers.file import get_human_readable_size, get_extension, get_type
try:
    from sqlalchemy import select, exists
except ImportError:
    pass


class Validator:
    def __init__(self, message):
        self.message = message

    async def __call__(self, value, meta):
        return None


class NotNull(Validator):
    def __init__(self, message='Null value'):
        super().__init__(message)

    async def __call__(self, value, meta):
        return None if value not in (None, '', b'') else self.message


class In(Validator):
    def __init__(self, values, message='Value error'):
        super().__init__(message)
        self.values = values

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        if value not in self.values:
            return self.message
        return None


class NotIn(Validator):
    def __init__(self, values, message='Value error'):
        super().__init__(message)
        self.values = values

    async def __call__(self, value, meta):
        if value in self.values:
            return self.message
        return None


class Length(Validator):
    def __init__(self, min=-1, max=-1, message='Length error'):
        super().__init__(message)
        self.min = min
        self.max = max
        if self.min != -1:
            self.message += ' min: %s' % self.min
        if self.max != -1:
            self.message += ' max: %s' % self.max

    async def __call__(self, value, meta):
        if value is None:
            return None
        value = str(value)
        if self.max != -1 and len(value) > self.max:
            return self.message
        elif self.min != -1 and len(value) < self.min:
            return self.message
        return None


class Limit(Validator):
    def __init__(self, min=None, max=None, message='Value limit error'):
        super().__init__(message)
        self.min = min
        self.max = max
        if self.min:
            self.message += ' min: %s' % self.min
        if self.max:
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
        if self.max and value and value > self.max:
            return self.message
        elif self.min and value and value < self.min:
            return self.message
        return None


class UUID(Validator):
    def __init__(self, message='Invalid UUID'):
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
    def __init__(self, message='Invalid email address'):
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
    def __init__(self, message='Must be numeric'):
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
    def __init__(self, message='Must be boolean'):
        super().__init__(message)

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        if value in (True, False, 'true', 'false'):
            return None
        return self.message


class Url(Validator):
    def __init__(self, message='Invalid URL'):
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
    def __init__(self, message='Invalid Path'):
        super().__init__(message)

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        if re.match(r'^/(([^/]*)((/[^/]+)*))$', value):
            return None
        return self.message


class PasswordStrength(Validator):
    def __init__(self, message='Weak password'):
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
    def __init__(self, message='Invalid date format (YYYY-MM-DD)'):
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
    def __init__(self, regex, message='Invalid format'):
        super().__init__(message)
        self.regex = regex
        
    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        if not self.regex:
            return None
        if re.match(self.regex, value):
            return None
        else:
            return self.message


class RestrictedFile(Validator):
    def __init__(self, extensions=None, max_size=-1, min_size=-1, message='File error'):
        super().__init__(message)
        self.extensions = extensions if extensions else tuple()
        self.max_size = -1
        self.min_size = -1
        if max_size != -1:
            self.max_size = float(max_size) * 1024.0
        if min_size != -1:
            self.min_size = float(min_size) * 1024.0

    async def __call__(self, value, meta):
        if value in (None, '', b''):
            return None
        f = value
        filename = None
        if isinstance(f, cgi.FieldStorage):
            if f.file:
                filename = f.filename
                if self.max_size != -1:
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
            if self.max_size != -1 and size > self.max_size:
                return '%s: %s %s' % (self.message, 'max size:', str(get_human_readable_size(self.max_size)))
            elif self.min_size != -1 and size < self.min_size:
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
    def __init__(self, model, model_field_name=None, except_self=None, except_default=False, case_sensitive=False,
                 message='Unique value error'):
        super().__init__(message)
        self.model = model
        self.model_field_name = model_field_name
        self.except_self = except_self
        self.except_default = except_default
        self.case_sensitive = case_sensitive

    async def __call__(self, value, meta):
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
    def __init__(self, inner_processors=None, message='Must be list'):
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