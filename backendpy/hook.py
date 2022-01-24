from inspect import iscoroutinefunction
from typing import Dict, List, Callable, AnyStr


class Hooks:
    def __init__(self):
        self._items: Dict[AnyStr, List[Callable]] = dict()

    @property
    def items(self):
        return self._items

    def register_event(self, name, func):
        assert iscoroutinefunction(func)
        self._register_event(name, func)

    def register_events(self, items: Dict[AnyStr, List[Callable]]):
        for name, funcs in items.items():
            for func in funcs:
                self.register_event(name, func)

    def event(self, name):
        def decorator_register_event(func):
            self.register_event(name, func)
        return decorator_register_event

    def merge(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'can not merge the "Hooks" and "{type(other)}"')
        for name, funcs in other.items.items():
            for func in funcs:
                self._register_event(name, func)

    def _register_event(self, name, func):
        if name not in self._items:
            self._items[name]: List[Callable] = list()
        self._items[name].append(func)

    def __getitem__(self, name):
        return self._items[name]

    def __contains__(self, name):
        return name in self._items

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'can not concat the "Hooks" and "{type(other)}"')
        new = self.__class__()
        new.register_events(self._items)
        new.register_events(other.items)
        return new


class HookRunner:
    def __init__(self):
        self.hooks = Hooks()

    async def execute(self, name, args=None):
        if name in self.hooks:
            for func in self.hooks[name]:
                if args is not None:
                    await func(**args)
                else:
                    await func()
