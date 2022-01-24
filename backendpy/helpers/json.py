from functools import singledispatch
from json import dumps  # ujson is faster but it is not safe in dumps
try:
    from ujson import loads
except ImportError:
    from json import loads


@singledispatch
def to_json(content):
    return dumps(content)


@to_json.register(str)
def _(content):
    return content


@to_json.register(bytes)
def _(content):
    return content


def from_json(content):
    return loads(content)
