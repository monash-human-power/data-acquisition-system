# Sourced from: https://github.com/micropython/micropython-lib/tree/master/abc
# This method is used with the Python's decorator (@) for tagging abstract methods
# Note: It is still WIP and so would not enforce that any method tagged with @abstractmethod be implemented in a sub
# class, but is used nevertheless to convey the intent


def abstractmethod(f):
    return f
