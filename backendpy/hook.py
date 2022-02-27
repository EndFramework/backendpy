from __future__ import annotations

from collections.abc import Mapping, Iterable
from inspect import iscoroutinefunction
from typing import Optional, Any


class Hooks:
    """Hook registry class"""

    def __init__(self) -> None:
        self._items: dict[str, list[callable]] = dict()

    @property
    def items(self) -> dict[str, list[callable]]:
        """Get registered event hooks."""
        return self._items

    def register(self, event_name: str, func: callable) -> None:
        """Register an event hook."""
        if not iscoroutinefunction(func):
            raise TypeError('The "func" parameter must be an asynchronous function.')
        self._register(event_name, func)

    def register_batch(self, items: Mapping[str, Iterable[callable]]) -> None:
        """Register multiple event hooks at once."""
        for event_name, funcs in items.items():
            for func in funcs:
                self.register(event_name, func)

    def event(self, name: str) -> callable:
        """Register an event hook with python decorator.

        :param name: The name of an event
        """
        def decorator_register(func: callable) -> None:
            self.register(name, func)
        return decorator_register

    def merge(self, other: Hooks) -> None:
        """Merge items from another Hooks class instance with this instance."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"{type(self.__class__)} and {type(other)} cannot be merged.")
        for event_name, funcs in other.items.items():
            for func in funcs:
                self._register(event_name, func)

    def _register(self, event_name: str, func: callable) -> None:
        if event_name not in self._items:
            self._items[event_name]: list[callable] = list()
        self._items[event_name].append(func)

    def __getitem__(self, name: str) -> list[callable]:
        return self._items[name]

    def __contains__(self, name: str) -> bool:
        return name in self._items

    def __add__(self, other: Hooks) -> Hooks:
        """Concatenate items from two instances of the Hooks class and return a new instance."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"{type(self.__class__)} and {type(other)} cannot be concatenated.")
        new = self.__class__()
        new.register_batch(self._items)
        new.register_batch(other.items)
        return new


class HookRunner:
    """Class for registering and triggering project hooks."""

    def __init__(self) -> None:
        self.hooks = Hooks()

    async def trigger(self, name: str, args: Optional[Mapping[str, Any]] = None) -> None:
        """Trigger all hooks related to the event.

        :param name: The name of an event
        :param args: A dictionary-like object containing arguments passed to the hook function.
        """
        if name in self.hooks:
            for func in self.hooks[name]:
                if args is not None:
                    await func(**args)
                else:
                    await func()
