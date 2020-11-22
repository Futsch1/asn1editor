from typing import Tuple, List, Optional

from asn1editor.interfaces.BitstringInterface import BitstringInterface
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import AbstractView, ContainerView, ListView, ChoiceView


class AbstractViewFactory:  # pragma: no cover
    def get_number_view(self, name: str, optional: bool, minimum: int, maximum: int, float_: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_text_view(self, name: str, text: str) -> AbstractView:
        raise NotImplementedError

    def get_container_view(self, name: str, optional: bool) -> Tuple[ContainerView, OptionalInterface]:
        raise NotImplementedError

    def get_list_view(self, name: str, minimum: int, maximum: int, optional: bool) -> Tuple[ListView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_enumerated_view(self, name: str, choices: List[str], optional: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_boolean_view(self, name: str, optional: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_hex_string_view(self, name: str, optional: bool, minimum: Optional[int], maximum: Optional[int]) -> \
            Tuple[ChoiceView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_string_view(self, name: str, string_type: str, optional: bool, minimum: int, maximum: int) -> Tuple[ChoiceView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_choice_view(self, name: str, choices: List[str], optional: bool) -> Tuple[ChoiceView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_bitstring_view(self, name: str, number_of_bits: int, named_bits: List[Tuple[int, str]], optional: bool) -> Tuple[ChoiceView, BitstringInterface,
                                                                                                                             OptionalInterface]:
        raise NotImplementedError
