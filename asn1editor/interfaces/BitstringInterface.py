import typing


class BitstringInterface:
    def get_values(self) -> typing.List[int]:
        raise NotImplementedError

    def set_values(self, values: typing.List[int]):
        raise NotImplementedError
