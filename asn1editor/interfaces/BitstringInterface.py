import typing


class BitstringInterface:  # pragma: no cover
    def get_values(self) -> typing.List[int]:
        raise NotImplementedError

    def set_values(self, values: typing.List[int]):
        raise NotImplementedError
