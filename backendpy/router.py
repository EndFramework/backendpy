import re
from typing import List


class Uri:
    def __init__(self, path, methods, handler, data_handler=None, only_ssl=False):
        self.path = re.compile(path, re.VERBOSE)
        self.methods = methods
        self.data_handler = data_handler
        self.handler = handler
        self.only_ssl = only_ssl


class Routes:
    def __init__(self, *args):
        self._items = list()
        for uri in args:
            self.append(uri)

    @property
    def items(self):
        return self._items

    def extend(self, routes: List[Uri]):
        if any(map(lambda uri: type(uri) is not Uri, routes)):
            raise ValueError
        self._items.extend(routes)

    def append(self, uri: Uri):
        if type(uri) is not Uri:
            raise ValueError
        self._items.append(uri)

    def merge(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'can not merge the "Routes" and "{type(other)}"')
        self._items.extend(other.items)

    def uri(self, path, methods, data_handler=None, only_ssl=False):
        def decorator_uri(handler):
            self.append(Uri(path, methods, handler, data_handler, only_ssl))
        return decorator_uri

    def __iter__(self):
        for r in self._items:
            yield r

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'can not concat the "Routes" and "{type(other)}"')
        return self.__class__().extend(self._items + other.items)


class Router:
    def __init__(self):
        self.routes = Routes()

    def match(self, path, method, scheme):
        for uri in self.routes:
            matched_path = uri.path.match(path)
            if matched_path and \
                    method in uri.methods and \
                    (scheme == 'https' or not uri.only_ssl):
                url_vars = matched_path.groupdict()
                return uri.handler, uri.data_handler, (url_vars if url_vars else None)
        else:
            return None, None, None
