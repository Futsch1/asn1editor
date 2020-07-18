from typing import Callable


class ValueInterface:
    def register_change_event(self, callback: Callable):
        raise NotImplementedError

    def get_value(self) -> str:
        raise NotImplementedError

    def set_value(self, val: str):
        raise NotImplementedError
