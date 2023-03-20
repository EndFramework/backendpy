from __future__ import annotations

import operator
import re
from collections.abc import Iterable
from typing import Type, Optional, AnyStr

from .data_handler.data import Data


class Route:
    """A class to define the specifications of a requestable URL path"""

    def __init__(
            self,
            path: str,
            methods: Iterable[str],
            handler: callable,
            data_handler = None,
            only_ssl: bool = False) -> None:
        """
        Initialize the route instance.

        :param path: Route path
        :param methods: List of acceptable HTTP methods for this route including
                        ``GET``, ``POST``, ``PUT``, ``PATCH``, ``DELETE``, ``HEAD`` & ``OPTIONS``
        :param handler: An async function that responds to requests to this route
        :param data_handler: A class of type :class:`~backendpy.data_handler.data.Data`
                             that processes input data before sending it to the handler function
        :param only_ssl: Determines whether only the https schema is acceptable
        """
        self.path = path
        self.methods = tuple(methods)
        self.data_handler = data_handler
        self.handler = handler
        self.only_ssl = only_ssl


class Routes:
    """A class for holding a list of :class:`~backendpy.router.Route`s"""

    def __init__(self, *args: Route) -> None:
        """
        Initialize the Routes instance.
        :param args: Instances of the :class:`~backendpy.router.Route` class as arguments
        """
        self._items: list[Route] = list()
        for route in args:
            self.append(route)

    def route(self,
              path: str,
              methods: Iterable[str],
              data_handler: Optional[Type[Data]] = None,
              only_ssl: bool = False) -> callable:
        """
        A decorator function to define route.
        .. seealso:: :class:`~backendpy.router.Route`
        """
        def decorator_route(handler: callable) -> None:
            self.append(Route(path, methods, handler, data_handler, only_ssl))
        return decorator_route

    def get(self,
            path: str,
            data_handler: Optional[Type[Data]] = None,
            only_ssl: bool = False) -> callable:
        """
        A decorator function to define route with ``GET`` method.
        .. seealso:: :class:`~backendpy.router.Route`
        """
        def decorator_get(handler: callable) -> None:
            self.append(Route(path, ("GET",), handler, data_handler, only_ssl))
        return decorator_get

    def post(self,
             path: str,
             data_handler: Optional[Type[Data]] = None,
             only_ssl: bool = False) -> callable:
        """
        A decorator function to define route with ``POST`` method.
        .. seealso:: :class:`~backendpy.router.Route`
        """
        def decorator_post(handler: callable) -> None:
            self.append(Route(path, ("POST",), handler, data_handler, only_ssl))
        return decorator_post

    def put(self,
            path: str,
            data_handler: Optional[Type[Data]] = None,
            only_ssl: bool = False) -> callable:
        """
        A decorator function to define route with ``PUT`` method.
        .. seealso:: :class:`~backendpy.router.Route`
        """
        def decorator_put(handler: callable) -> None:
            self.append(Route(path, ("PUT",), handler, data_handler, only_ssl))
        return decorator_put

    def patch(self,
              path: str,
              data_handler: Optional[Type[Data]] = None,
              only_ssl: bool = False) -> callable:
        """
        A decorator function to define route with ``PATCH`` method.
        .. seealso:: :class:`~backendpy.router.Route`
        """
        def decorator_patch(handler: callable) -> None:
            self.append(Route(path, ("PATCH",), handler, data_handler, only_ssl))
        return decorator_patch

    def delete(self,
               path: str,
               data_handler: Optional[Type[Data]] = None,
               only_ssl: bool = False) -> callable:
        """
        A decorator function to define route with ``DELETE`` method.
        .. seealso:: :class:`~backendpy.router.Route`
        """
        def decorator_delete(handler: callable) -> None:
            self.append(Route(path, ("DELETE",), handler, data_handler, only_ssl))
        return decorator_delete

    def head(self,
             path: str,
             data_handler: Optional[Type[Data]] = None,
             only_ssl: bool = False) -> callable:
        """
        A decorator function to define route with ``HEAD`` method.

        .. seealso:: :class:`~backendpy.router.Route`
        """
        def decorator_delete(handler: callable) -> None:
            self.append(Route(path, ("HEAD",), handler, data_handler, only_ssl))
        return decorator_delete

    def options(self,
                path: str,
                data_handler: Optional[Type[Data]] = None,
                only_ssl: bool = False) -> callable:
        """
        A decorator function to define route with ``OPTIONS`` method.

        .. seealso:: :class:`~backendpy.router.Route`
        """
        def decorator_delete(handler: callable) -> None:
            self.append(Route(path, ("OPTIONS",), handler, data_handler, only_ssl))
        return decorator_delete

    @property
    def items(self) -> list[Route]:
        """Get routes list"""
        return self._items

    def extend(self, routes: Iterable[Route]) -> None:
        """Extend items"""
        if any(map(lambda route: type(route) is not Route, routes)):
            raise ValueError("Invalid route type")
        self._items.extend(routes)

    def append(self, route: Route) -> None:
        """Append to items"""
        if type(route) is not Route:
            raise ValueError("Invalid route type")
        self._items.append(route)

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


class TrieNode:
    """A class to define the trie tree node."""

    def __init__(self) -> None:
        """ Initialize the trie tree."""
        self._children: dict[str, TrieNode] = dict()
        self._pattern_children: dict[re.Pattern, TrieNode] = dict()
        self.route: Optional[dict] = None
        self.priority_order: Optional[list[int]] = None

    def get_candidate_nodes(self, key: str, remaining_count: int) -> list[TrieNode]:
        nodes = []
        ch = self._children.get(key)
        if ch is not None \
                and (remaining_count > 1 or ch.route is not None):
            nodes.append(ch)
        if self._pattern_children:
            for pattern, ch in self._pattern_children.items():
                if remaining_count > 1 or ch.route is not None:
                    if pattern.fullmatch(key):
                        nodes.append(ch)
        return nodes

    def set_default_node(self, key: str):
        if key not in self._children:
            self._children[key] = TrieNode()
        return self._children[key]

    def set_default_pattern_node(self, pattern: re.Pattern):
        if pattern not in self._pattern_children:
            self._pattern_children[pattern] = TrieNode()
        return self._pattern_children[pattern]


class Router:
    """A class for routing requests based on the trie tree of routes path parts."""

    def __init__(self) -> None:
        """
        Initialize the router trees root node.
        """
        self._route_tree_root: dict[str, TrieNode] = {
            'GET': TrieNode(),
            'POST': TrieNode(),
            'PATCH': TrieNode(),
            'PUT': TrieNode(),
            'DELETE': TrieNode(),
            'OPTIONS': TrieNode(),
            'HEAD': TrieNode()}

    @staticmethod
    def _is_var_part(part: str):
        return part.startswith('<') and part.endswith('>')

    @staticmethod
    def _is_pattern_part(part: str):
        return part.startswith('(') and part.endswith(')')

    def append(self, route: Route):
        for method in route.methods:
            curr = self._route_tree_root[method]
            if route.path in ('/', ''):
                curr.route = {
                    'handler': route.handler,
                    'data_handler': route.data_handler,
                    'ssl': route.only_ssl}
            else:
                route_path_parts = route.path.split('/')
                var_indexes = {}
                priority_order = []
                for i, part in enumerate(route_path_parts):
                    if part:
                        if self._is_var_part(part):
                            part = part[1:-1]
                            var_name, var_type = part.split(':', 1) if ':' in part else (part, 'str')
                            if var_type in PREDEFINED_REGEXES:
                                pattern = PREDEFINED_REGEXES[var_type]
                            elif self._is_pattern_part(var_type):
                                try:
                                    pattern = re.compile(var_type)
                                except re.error:
                                    raise ValueError(f'Invalid regex pattern in the route path: "{route.path}"')
                            else:
                                raise ValueError(f'Invalid var type in the route path: "{route.path}"')
                            curr = curr.set_default_pattern_node(pattern)
                            priority_order.append(0)
                            var_indexes[var_name] = i
                        elif self._is_pattern_part(part):
                            try:
                                curr = curr.set_default_pattern_node(re.compile(part))
                                priority_order.append(0)
                            except re.error:
                                raise ValueError(f'Invalid regex pattern in the route path: "{route.path}"')
                        else:
                            curr = curr.set_default_node(part)
                            priority_order.append(1)
                curr.route = {
                    'handler': route.handler,
                    'data_handler': route.data_handler,
                    'path_var_indexes': var_indexes,
                    'ssl': route.only_ssl}
                curr.priority_order = priority_order

    def extend(self, routes: Iterable[Route] | Routes):
        for route in routes:
            self.append(route)

    def lookup(self, path: str, method: str, scheme: str) \
            -> tuple[Optional[callable], Optional[Type[Data]], Optional[dict[str, AnyStr]]]:
        """
        Match the request information with the corresponding route and return the route handlers.
        :param path: Http request path
        :param method: Http request method
        :param scheme: Http request scheme
        :return: A tuple that includes a request handler function, data handler class, and path variables dict.
        """
        curr = [self._route_tree_root[method]]
        if path in ('/', ''):
            return (curr[0].route['handler'], curr[0].route['data_handler'], None) \
                if curr[0].route is not None and (not curr[0].route['ssl'] or scheme == 'https') \
                else (None, None, None)
        else:
            parts = path.split('/')
            parts_size = len(parts)
            for i, part in enumerate(parts):
                if part:
                    candidates = []
                    for c in curr:
                        candidates += c.get_candidate_nodes(
                            part,
                            remaining_count=parts_size-i)
                    if not candidates:
                        return None, None, None
                    curr = candidates
            if len(curr) == 1:
                curr = curr[0]
            else:
                curr = max(curr, key=operator.attrgetter('priority_order'))
            if curr.route['ssl'] and scheme != 'https':
                return None, None, None
            path_vars = {key: parts[index] for key, index in curr.route['path_var_indexes'].items()}
            return curr.route['handler'], curr.route['data_handler'], (path_vars if path_vars else None)


PREDEFINED_REGEXES = {
    'str': re.compile(r'^(\w+)$'),
    'int': re.compile(r'^([-+]?\d+)$'),
    'float': re.compile(r'^([-+]?\d+\.\d+)$'),
    'uuid': re.compile(r'^([0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12})$'),
    'slug': re.compile(r'^([-\w]+)$'),
    # Todo: 'path'
    # Todo: 'any_of(a|b|c)'
}
