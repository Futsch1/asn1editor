from typing import Callable


class OptionalInterface:  # pragma: no cover
    """
    Interface for optional elements.

    Needs to be provided by the view factory that creates the elements.
    """

    def register_optional_event(self, callback: Callable):
        """
        Called by the controller to register a callback that needs to be called whenever the optional status of an element changes.
        """
        raise NotImplementedError

    def get_has_value(self) -> bool:
        raise NotImplementedError

    def set_has_value(self, val: bool):
        raise NotImplementedError

    def get_default_has_value(self) -> bool:
        raise NotImplementedError
