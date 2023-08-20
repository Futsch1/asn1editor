import typing


class BitstringInterface:  # pragma: no cover
    """
    Interface for a bit string view to get and set selected bit string values.

    Needs to be provided by the view factory that creates the bit string view.
    """

    def get_values(self) -> typing.List[int]:
        raise NotImplementedError

    def set_values(self, values: typing.List[int]):
        raise NotImplementedError
