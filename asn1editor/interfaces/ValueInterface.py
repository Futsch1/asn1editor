import typing


class ValueInterface:  # pragma: no cover
    """
    Interface for a value view to get and set the values and handle changes.

    Needs to be provided by the view factory that creates a value view.
    """

    def register_change_event(self, callback: typing.Callable):
        """
        Called by the controller to register a callback that needs to be called whenever the value of an element changes.
        """
        raise NotImplementedError

    def get_value(self) -> typing.Union[str, bytes, bool]:
        raise NotImplementedError

    def set_value(self, val: typing.Union[str, bytes, bool]):
        raise NotImplementedError
