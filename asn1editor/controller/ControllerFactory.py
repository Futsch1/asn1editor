from typing import Optional

from asn1tools.codecs import oer

from asn1editor.controller import Controller, Converter
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface


class ControllerFactory:
    def __init__(self, parent: Controller):
        self._parent = parent

    def create_value_controller(self, type_: oer.Type, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface]):
        if isinstance(type_, oer.Integer):
            controller = Controller.ValueController(type_.name, self._parent, value_interface, optional_interface, Converter.Int(), type_.default)
        elif isinstance(type_, oer.Real):
            controller = Controller.ValueController(type_.name, self._parent, value_interface, optional_interface, Converter.Float(), type_.default)
        elif isinstance(type_, oer.Enumerated):
            if type_.default is None:
                default = sorted(type_.value_to_data.values())[0]
            else:
                default = type_.default
            controller = Controller.ValueController(type_.name, self._parent, value_interface, optional_interface, Converter.Str(), default)
        elif type(type_) in [oer.OctetString, oer.UTF8String, oer.VisibleString, oer.GeneralString]:
            # noinspection PyTypeChecker
            encoding = {oer.OctetString: 'ascii', oer.UTF8String: 'utf-8', oer.VisibleString: 'ascii', oer.GeneralString: 'latin1'}[type(type_)]
            controller = Controller.ValueController(type_.name, self._parent, value_interface, optional_interface, Converter.ByteString(encoding),
                                                    type_.default)
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
            controller = Controller.ChoiceController(type_.name, self._parent, value_interface, optional_interface, default, choice_instance_factory)
            self.__register_events(controller, value_interface, optional_interface)
        else:
            raise Exception(f"Unknown type for ControllerFactory: {type_}")

    @staticmethod
    def __register_events(controller: Controller.Controller, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface]):
        value_interface.register_change_event(controller.event_handler)
        if optional_interface is not None:
            optional_interface.register_optional_event(controller.optional_handler)
