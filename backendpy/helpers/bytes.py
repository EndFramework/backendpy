from functools import singledispatch


@singledispatch
def to_bytes(content):
    return str(content).encode('utf-8')


@to_bytes.register(str)
def _(content):
    return content.encode('utf-8')


@to_bytes.register(bytes)
def _(content):
    return content
