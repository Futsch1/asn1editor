from typing import Optional, Union

from asn1tools.codecs import oer

from asn1editor.controller import Controller, Converter
from asn1editor.interfaces.BitstringInterface import BitstringInterface
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface


class ControllerFactory:
    def __init__(self, parent: Controller):
        self._parent = parent

    def create_value_controller(self, type_: oer.Type, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface],
                                minimum: Union[str, int, float] = 0):
        if isinstance(type_, oer.Integer):
            controller = Controller.ValueController(type_.name, self._parent, value_interface, optional_interface, Converter.Int(minimum, type_.default))
        elif isinstance(type_, oer.Real):
            controller = Controller.ValueController(type_.name, self._parent, value_interface, optional_interface, Converter.Float(minimum, type_.default))
        elif isinstance(type_, oer.Enumerated):
            if type_.default is None:
                default = sorted(type_.value_to_data.values())[0]
            else:
                default = type_.default
            controller = Controller.ValueController(type_.name, self._parent, value_interface, optional_interface, Converter.Str(0, default))
        elif type(type_) in [oer.UTF8String, oer.VisibleString, oer.GeneralString]:
            # noinspection PyTypeChecker
            # encoding = {oer.OctetString: 'ascii', oer.UTF8String: 'utf-8', oer.VisibleString: 'ascii', oer.GeneralString: 'latin1'}[type(type_)]
            controller = Controller.ValueController(type_.name, self._parent, value_interface, optional_interface, Converter.Str(minimum, type_.default))
        elif isinstance(type_, oer.OctetString):
            controller = Controller.ValueController(type_.name, self._parent, value_interface, optional_interface, Converter.ByteString(minimum, type_.default))
        else:
            raise Exception(f"Unknown type for ControllerFactory: {type_}")

        self.__register_events(controller, value_interface, optional_interface)

    def create_container_controller(self, type_: oer.Type, optional_interface: Optional[OptionalInterface]) -> Controller.ContainerController:
        if isinstance(type_, oer.Sequence):
            controller = Controller.ContainerController(type_.name, self._parent, optional_interface)
            if optional_interface is not None:
                optional_interface.register_optional_event(controller.optional_handler)

            return controller
        else:
            raise Exception(f"Unknown type for ControllerFactory: {type_}")

    def create_list_controller(self, type_: oer.Type, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface], list_instance_factory,
                               minimum_elements: int):
        if isinstance(type_, oer.SequenceOf):
            controller = Controller.ListController(type_.name, self._parent, value_interface, optional_interface, list_instance_factory, minimum_elements)
            self.__register_events(controller, value_interface, optional_interface)
        else:
            raise Exception(f"Unknown type for ControllerFactory: {type_}")

    def create_bool_controller(self, type_: oer.Type, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface]):
        if isinstance(type_, oer.Boolean):
            controller = Controller.BoolController(type_.name, self._parent, value_interface, optional_interface, type_.default)
            self.__register_events(controller, value_interface, optional_interface)
        else:
            raise Exception(f"Unknown type for ControllerFactory: {type_}")

    def create_choice_controller(self, type_: oer.Type, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface],
                                 choice_instance_factory):
        if isinstance(type_, oer.Choice):
            if type_.default is None:
                default = sorted([member.name for member in type_.members])[0]
            else:
                default = type_.default
            controller = Controller.ChoiceController(type_.name, self._parent, value_interface, optional_interface, choice_instance_factory, default)
            self.__register_events(controller, value_interface, optional_interface)
        else:
            raise Exception(f"Unknown type for ControllerFactory: {type_}")

    def create_bitstring_controller(self, type_: oer.Type, bitstring_interface: BitstringInterface, optional_interface: Optional[OptionalInterface]):
        if isinstance(type_, oer.BitString):
            controller = Controller.BitstringController(type_.name, self._parent, bitstring_interface, optional_interface, type_.number_of_bits)
            if optional_interface is not None:
                optional_interface.register_optional_event(controller.optional_handler)
        else:
            raise Exception(f"Unknown type for ControllerFactory: {type_}")

    @staticmethod
    def __register_events(controller: Controller.Controller, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface]):
        value_interface.register_change_event(controller.event_handler)
        if optional_interface is not None:
            optional_interface.register_optional_event(controller.optional_handler)
