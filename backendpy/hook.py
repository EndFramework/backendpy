from inspect import iscoroutinefunction
from typing import Dict, List, Callable, AnyStr


class Hooks:
    def __init__(self):
        self._items: Dict[AnyStr, List[Callable]] = dict()

    @property
    def items(self):
        return self._items

    def register(self, event_name, func):
        assert iscoroutinefunction(func)
        self._register(event_name, func)

    def register_batch(self, items: Dict[AnyStr, List[Callable]]):
        for event_name, funcs in items.items():
            for func in funcs:
                self.register(event_name, func)

    def event(self, name):
        def decorator_register(func):
            self.register(name, func)
        return decorator_register

    def merge(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'Can not merge the "Hooks" and "{type(other)}"')
        for event_name, funcs in other.items.items():
            for func in funcs:
                self._register(event_name, func)

    def _register(self, event_name, func):
        if event_name not in self._items:
            self._items[event_name]: List[Callable] = list()
        self._items[event_name].append(func)

    def __getitem__(self, name):
        return self._items[name]

    def __contains__(self, name):
        return name in self._items

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'Can not concat the "Hooks" and "{type(other)}"')
        new = self.__class__()
        new.register_batch(self._items)
        new.register_batch(other.items)
        return new


class HookRunner:
    def __init__(self):
        self.hooks = Hooks()

    async def trigger(self, name, args=None):
        if name in self.hooks:
            for func in self.hooks[name]:
                if args is not None:
                    await func(**args)
                else:
                    await func()
