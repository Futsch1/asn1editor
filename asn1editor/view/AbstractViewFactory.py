import typing
from enum import IntFlag
from typing import Tuple, List, Optional

from asn1editor.interfaces.BitstringInterface import BitstringInterface
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import AbstractView, ContainerView, ListView, ChoiceView


class Styles(IntFlag):
    """
    Styling flags to change the look of elements
    READ_ONLY means that the element shall not be modifiable, indicating that the GUI elements shall be read only.
    HIDDEN means that the element's data will be part of the model, but it shall not appear on the GUI
    """
    READ_ONLY = 1
    HIDDEN = 2


class TypeInfo:
    """
    Represents the info of an ASN.1 type required to create corresponding GUI controls

    name: Name of the element
    tag: ASN.1 tag
    typename: Type of the underlying ASN.1 type
    optional: If set, the element may be present or not
    additional: If set, the element is part of the additional elements in an ASN.1 spec
    style: Additional styling flags
    help: Optional help string
    """
    name: str = ''
    tag: str = ''
    typename: str = ''
    optional: bool = False
    additional: bool = False
    style: Styles = 0
    help: typing.Optional[str] = None


class AbstractViewFactory:  # pragma: no cover
    """
    Creates views for all types.

    Depending on the type of view, further interfaces are returned to be used by the controllers to read and write the view's contents.
    """

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
            Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_string_view(self, type_info: TypeInfo, minimum: int, maximum: int) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_choice_view(self, type_info: TypeInfo, choices: List[str]) -> Tuple[ChoiceView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_bitstring_view(self, type_info: TypeInfo, number_of_bits: int, named_bits: List[Tuple[int, str]]) -> \
            Tuple[AbstractView, BitstringInterface, OptionalInterface]:
        raise NotImplementedError

    def get_date_view(self, type_info: TypeInfo) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_time_view(self, type_info: TypeInfo) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError

    def get_datetime_view(self, type_info: TypeInfo) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        raise NotImplementedError
