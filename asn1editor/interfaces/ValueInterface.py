import typing


class ValueInterface:  # pragma: no cover
    def register_change_event(self, callback: typing.Callable):
        raise NotImplementedError

    def get_value(self) -> typing.Union[str, bytes, bool]:
        raise NotImplementedError

    def set_value(self, val: typing.Union[str, bytes, bool]):
        raise NotImplementedError
