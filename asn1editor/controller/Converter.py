import typing
from datetime import date, time


class Converter:
    """
    Converts values from view to model and vice versa. GUI implementations usually work with strings, while the ASN.1 model requires numeric data types.
    """

    def __init__(self, minimum: typing.Optional[typing.Union[int, float]], default: typing.Optional[typing.Union[str, bytes, int, float, date, time]]):
        self._default = default
        self._minimum = minimum
        if self._minimum is None:
            self._minimum = 0

    @staticmethod
    def to_view(val: typing.Any) -> typing.Union[str, bytes]:  # pragma: no cover
        raise NotImplementedError

    @staticmethod
    def from_view(val: typing.Union[str, bytes]) -> typing.Any:  # pragma: no cover
        raise NotImplementedError

    @staticmethod
    def default() -> typing.Union[str, bytes, int, float]:  # pragma: no cover
        raise NotImplementedError


class Str(Converter):
    @staticmethod
    def to_view(val: str) -> str:
        return val

    @staticmethod
    def from_view(val: str) -> str:
        return val

    def default(self) -> str:
        return ' ' * self._minimum if not self._default else self._default


class Any(Converter):
    @staticmethod
    def to_view(val: typing.Any) -> typing.Any:
        return val

    @staticmethod
    def from_view(val: typing.Any) -> typing.Any:
        return val

    def default(self) -> typing.Any:
        return self._default


class Int(Converter):
    @staticmethod
    def to_view(val: int) -> str:
        return str(val)

    @staticmethod
    def from_view(val: str) -> int:
        try:
            i = int(val)
        except ValueError:
            i = 0
        return i

    def default(self) -> int:
        return self._minimum if not self._default else self.from_view(self._default)


class Float(Converter):
    @staticmethod
    def to_view(val: float) -> str:
        return str(val)

    @staticmethod
    def from_view(val: str) -> float:
        try:
            i = float(val)
        except ValueError:
            i = 0
        return i

    def default(self) -> float:
        return self._minimum if not self._default else self._default


class ByteString(Converter):
    @staticmethod
    def to_view(val: bytes) -> bytes:
        return val

    @staticmethod
    def from_view(val: bytes) -> bytes:
        return val

    def default(self) -> bytes:
        if isinstance(self._default, str):
            self._default = self._default.encode('latin-1')
        return b' ' * self._minimum if not self._default else self._default
