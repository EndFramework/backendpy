from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Type, Optional, AnyStr

from .data_handler.data import Data


class Uri:
    """A class to define the specifications of a route."""

    def __init__(
            self,
            path: str,
            methods: Iterable[str],
            handler: callable,
            data_handler: Optional[Type[Data]] = None,
            only_ssl: bool = False) -> None:
        """
        Initialize the Uri instance.

        :param path: Uri path in regular expression format
        :param methods: List of acceptable HTTP methods for this Uri
                        including ``GET``, ``POST``, ``PUT``, ``PATCH`` & ``DELETE``
        :param handler: An Async function that responds to requests to this Uri
        :param data_handler: A class of type :class:`~backendpy.data_handler.data.Data`
                             that processes input data before sending it to the handler function
        :param only_ssl: Determines whether only the https schema is acceptable
        """
        self.path = re.compile(path, re.VERBOSE)
        self.methods = tuple(methods)
        self.data_handler = data_handler
        self.handler = handler
        self.only_ssl = only_ssl


class Routes:
    """A class for holding a list of Uri."""

    def __init__(self, *args: Uri) -> None:
        """
        Initialize the Routes instance.

        :param args: Instances of the :class:`~backendpy.router.Uri` class as arguments
        """
        self._items: list[Uri] = list()
        for uri in args:
            self.append(uri)

    def uri(self,
            path: str,
            methods: Iterable[str],
            data_handler: Optional[Type[Data]] = None,
            only_ssl: bool = False) -> callable:
        """
        A decorator function to define Uri.

        .. seealso:: :class:`~backendpy.router.Uri`
        """
        def decorator_uri(handler: callable) -> None:
            self.append(Uri(path, methods, handler, data_handler, only_ssl))
        return decorator_uri

    def get(self,
            path: str,
            data_handler: Optional[Type[Data]] = None,
            only_ssl: bool = False) -> callable:
        """
        A decorator function to define Uri with ``GET`` method.

        .. seealso:: :class:`~backendpy.router.Uri`
        """
        def decorator_get(handler: callable) -> None:
            self.append(Uri(path, ("GET",), handler, data_handler, only_ssl))
        return decorator_get

    def post(self,
             path: str,
             data_handler: Optional[Type[Data]] = None,
             only_ssl: bool = False) -> callable:
        """
        A decorator function to define Uri with ``POST`` method.

        .. seealso:: :class:`~backendpy.router.Uri`
        """
        def decorator_post(handler: callable) -> None:
            self.append(Uri(path, ("POST",), handler, data_handler, only_ssl))
        return decorator_post

    def put(self,
            path: str,
            data_handler: Optional[Type[Data]] = None,
            only_ssl: bool = False) -> callable:
        """
        A decorator function to define Uri with ``PUT`` method.

        .. seealso:: :class:`~backendpy.router.Uri`
        """
        def decorator_put(handler: callable) -> None:
            self.append(Uri(path, ("PUT",), handler, data_handler, only_ssl))
        return decorator_put

    def patch(self,
              path: str,
              data_handler: Optional[Type[Data]] = None,
              only_ssl: bool = False) -> callable:
        """
        A decorator function to define Uri with ``PATCH`` method.

        .. seealso:: :class:`~backendpy.router.Uri`
        """
        def decorator_patch(handler: callable) -> None:
            self.append(Uri(path, ("PATCH",), handler, data_handler, only_ssl))
        return decorator_patch

    def delete(self,
               path: str,
               data_handler: Optional[Type[Data]] = None,
               only_ssl: bool = False) -> callable:
        """
        A decorator function to define Uri with ``DELETE`` method.

        .. seealso:: :class:`~backendpy.router.Uri`
        """
        def decorator_delete(handler: callable) -> None:
            self.append(Uri(path, ("DELETE",), handler, data_handler, only_ssl))
        return decorator_delete

    @property
    def items(self) -> list[Uri]:
        """Get items list"""
        return self._items

    def extend(self, routes: Iterable[Uri]) -> None:
        """Extend items"""
        if any(map(lambda uri: type(uri) is not Uri, routes)):
            raise ValueError("Invalid Uri type")
        self._items.extend(routes)

    def append(self, uri: Uri) -> None:
        """Append to items"""
        if type(uri) is not Uri:
            raise ValueError("Invalid Uri type")
        self._items.append(uri)

    def merge(self, other: Routes) -> None:
        """Merge items from another Routes class instance with this instance."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"{type(self.__class__)} and {type(other)} cannot be merged.")
        self._items.extend(other.items)

    def __iter__(self):
        """Iter items"""
        yield from self._items

    def __add__(self, other: Routes) -> Routes:
        """Concatenate items from two instances of the Routes class and return a new instance."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"{type(self.__class__)} and {type(other)} cannot be concatenated.")
        return self.__class__(*(self._items + other.items))


class Router:
    """A class for routing requests."""

    def __init__(self) -> None:
        self.routes = Routes()

    def match(self, path: str, method: str, scheme: str) \
            -> tuple[Optional[callable], Optional[Type[Data]], Optional[dict[str, AnyStr]]]:
        """
        Match the request information with the corresponding Uri and return the Uri handlers.

        :param path: Http request URI path
        :param method: Http request method
        :param scheme: Http request URI scheme
        :return: A tuple that includes a request handler function, data handler class, and URI variables dict.
        """
        for uri in self.routes:
            matched_path = uri.path.match(path)
            if matched_path and \
                    method in uri.methods and \
                    (scheme == 'https' or not uri.only_ssl):
                url_vars = matched_path.groupdict()
                return uri.handler, uri.data_handler, (url_vars if url_vars else None)
        else:
            return None, None, None
