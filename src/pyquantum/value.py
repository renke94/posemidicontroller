from typing import List, Union, Set, Tuple


class Value:
    def __init__(self, data, _children=()):
        self.data = data
        self.subscribers = set()
        self.subscriptions = set(_children)
        for publisher in self.subscriptions:
            publisher.subscribe(self)
        self.update_callbacks = []

    @property
    def dtype(self):
        return type(self.data)

    def set_data(self, data: any):
        is_different = self.data != data
        self.data = data
        if is_different:
            self.notify_subscribers()

    def subscribe(self, value):
        self.subscribers.add(value)

    def unsubscribe(self, value):
        self.subscribers.remove(value)

    def notify_subscribers(self):
        for sub in self.subscribers:
            sub.value_update(self.data)

    def on_update(self, callback):
        self.update_callbacks.append(callback)

    def value_update(self, data):
        for callback in self.update_callbacks:
            callback(data)

    def __del__(self):
        for publisher in self.subscriptions:
            publisher.unsubscribe(self)

    def __repr__(self):
        return f"Value({self.data}, dtype={self.dtype})"

    def map(self, function):
        out = Value(function(self.data), _children=(self,))

        def on_update(data):
            out.set_data(function(self.data))

        out.on_update(on_update)
        return out

    def __generic_operation__(self, other, function):
        if isinstance(other, Value):
            out = Value(function(self.data, other.data), _children=(self, other))

            def on_update(data):
                out.set_data(function(self.data, other.data))

        else:
            out = Value(function(self.data, other), _children=(self,))

            def on_update(data):
                out.set_data(function(self.data, other))

        out.on_update(on_update)
        return out

    def __add__(self, other):
        return self.__generic_operation__(other, lambda a, b: a + b)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self.__generic_operation__(other, lambda a, b: a - b)

    def __rsub__(self, other):
        return self.__generic_operation__(other, lambda a, b: b - a)

    def __mul__(self, other):
        return self.__generic_operation__(other, lambda a, b: a * b)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        return self.__generic_operation__(other, lambda a, b: a / b)

    def __rtruediv__(self, other):
        return self.__generic_operation__(other, lambda a, b: b / a)

    def __neg__(self):
        return self.map(lambda x: -x)

    def __and__(self, other):
        return self.__generic_operation__(other, lambda a, b: a & b)

    def __rand__(self, other):
        return self & other

    def __or__(self, other):
        return self.__generic_operation__(other, lambda a, b: a | b)

    def __ror__(self, other):
        return self | other

    def __lt__(self, other):
        return self.__generic_operation__(other, lambda a, b: a < b)

    def __le__(self, other):
        return self.__generic_operation__(other, lambda a, b: a <= b)

    def __gt__(self, other):
        return self.__generic_operation__(other, lambda a, b: a > b)

    def __ge__(self, other):
        return self.__generic_operation__(other, lambda a, b: a >= b)

    def __invert__(self):
        return self.map(lambda x: (not x) if isinstance(x, bool) else ~x)

    def eq(self, other):
        return self.__generic_operation__(other, lambda a, b: a == b)


class Observer:
    def __init__(self, observables: Union[List[Value], Set[Value], Tuple[Value]]):
        self.observables = observables
        for observable in self.observables:
            observable.subscribe(self)
        self.update_callbacks = []

    def on_update(self, callback):
        self.update_callbacks.append(callback)

    def value_update(self, value):
        for callback in self.update_callbacks:
            callback(value)

    def __del__(self):
        for observable in self.observables:
            observable.unsubscribe(self)