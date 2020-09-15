# Sourced from: https://github.com/micropython/micropython-lib/tree/master/abc
# This method is used with Python's decorator (@) for tagging abstract methods in MicroPython (which doesn't have a
# built-in ABC module).
# Note: It is still WIP and so would not enforce that any method tagged with @abstractmethod be implemented in a sub
# class, but is used nevertheless to convey the intent


def abstractmethod(f):
    return f
