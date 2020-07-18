from typing import Any


class Converter:
    @staticmethod
    def to_str(val: Any) -> str:
        raise NotImplementedError

    @staticmethod
    def from_str(val: str) -> Any:
        raise NotImplementedError


class Str(Converter):
    @staticmethod
    def to_str(val: str) -> str:
        return val

    @staticmethod
    def from_str(val: str) -> str:
        return val


class Int(Converter):
    @staticmethod
    def to_str(val: int) -> str:
        return str(val)

    @staticmethod
    def from_str(val: str) -> int:
        try:
            i = int(val)
        except ValueError:
            i = 0
        return i


class Float(Converter):
    @staticmethod
    def to_str(val: float) -> str:
        return str(val)

    @staticmethod
    def from_str(val: str) -> float:
        try:
            i = float(val)
        except ValueError:
            i = 0
        return i


class ByteString(Converter):
    def __init__(self, encoding):
        self._encoding = encoding

    def to_str(self, val: bytes) -> str:
        return val.decode(self._encoding)

    def from_str(self, val: str) -> bytes:
        return val.encode(self._encoding)
