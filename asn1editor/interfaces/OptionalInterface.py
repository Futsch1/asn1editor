from typing import Callable


class OptionalInterface:  # pragma: no cover
    def register_optional_event(self, callback: Callable):
        raise NotImplementedError

    def get_has_value(self) -> bool:
        raise NotImplementedError

    def set_has_value(self, val: bool):
        raise NotImplementedError
