import typing
from enum import IntFlag
from typing import Tuple, List, Optional

from asn1editor.interfaces.BitstringInterface import BitstringInterface
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import AbstractView, ContainerView, ListView, ChoiceView


class Styles(IntFlag):
    READ_ONLY = 1
    HIDDEN = 2


class TypeInfo:
    name: str = ''
    tag: str = ''
    typename: str = ''
    optional: bool = False
    additional: bool = False
    style: Styles = 0
    help: typing.Optional[str] = None


class AbstractViewFactory:  # pragma: no cover
    def get_number_view(self, type_info: TypeInfo, minimum: int, maximum: int, float_: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_text_view(self, type_info: TypeInfo, text: str) -> AbstractView:
        raise NotImplementedError

    def get_container_view(self, type_info: TypeInfo) -> Tuple[ContainerView, OptionalInterface]:
        raise NotImplementedError

    def get_list_view(self, type_info: TypeInfo, minimum: int, maximum: int) -> Tuple[ListView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_enumerated_view(self, type_info: TypeInfo, choices: List[str]) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_boolean_view(self, type_info: TypeInfo) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_hex_string_view(self, type_info: TypeInfo, minimum: Optional[int], maximum: Optional[int]) -> \
            Tuple[ChoiceView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_string_view(self, type_info: TypeInfo, minimum: int, maximum: int) -> Tuple[ChoiceView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_choice_view(self, type_info: TypeInfo, choices: List[str]) -> Tuple[ChoiceView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_bitstring_view(self, type_info: TypeInfo, number_of_bits: int, named_bits: List[Tuple[int, str]]) -> Tuple[ChoiceView, BitstringInterface,
                                                                                                                       OptionalInterface]:
        raise NotImplementedError

    def get_date_view(self, type_info: TypeInfo) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_time_view(self, type_info: TypeInfo) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_datetime_view(self, type_info: TypeInfo) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError
