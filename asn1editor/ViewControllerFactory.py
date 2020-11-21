from typing import Tuple, Union, Any

from asn1tools.codecs import constraints_checker
from asn1tools.compiler import oer

from asn1editor.controller.ChoiceInstanceFactory import ChoiceInstanceFactory
from asn1editor.controller.Controller import Controller, RootController
from asn1editor.controller.ControllerFactory import ControllerFactory
from asn1editor.controller.ListInstanceFactory import ListInstanceFactory
from asn1editor.view.AbstractView import AbstractView
from asn1editor.view.AbstractViewFactory import AbstractViewFactory


class ViewControllerFactory(object):
    def __init__(self, view_factory: AbstractViewFactory):
        self._view_factory = view_factory

    def create(self, asn1_type: oer.CompiledType) -> Tuple[AbstractView, Controller]:
        controller = RootController('root')
        view = self.create_view_and_controller(asn1_type.type, asn1_type.constraints_checker.type, controller)

        return view, controller

    def create_view_and_controller(self, type_: oer.Type, checker: constraints_checker.Type, controller: Controller) -> AbstractView:
        if isinstance(type_, oer.Integer):
            return self._number(type_, checker, controller)
        elif isinstance(type_, oer.Boolean):
            return self._bool(type_, controller)
        elif isinstance(type_, oer.Real):
            return self._number(type_, checker, controller)
        elif isinstance(type_, oer.Sequence) or isinstance(type_, oer.Set):
            # noinspection PyTypeChecker
            return self._sequence(type_, checker, controller)
        elif isinstance(type_, oer.SequenceOf) or isinstance(type_, oer.SetOf):
            # noinspection PyTypeChecker
            return self._sequence_of(type_, checker, controller)
        elif isinstance(type_, oer.Choice):
            # noinspection PyTypeChecker
            return self._choice(type_, checker, controller)
        elif isinstance(type_, oer.OctetString):
            # noinspection PyTypeChecker
            return self._hex_string(type_, checker, controller)
        elif type(type_) in [oer.UTF8String, oer.VisibleString, oer.GeneralString, oer.IA5String, oer.ObjectIdentifier]:
            # noinspection PyTypeChecker
            return self._string(type_, checker, controller)
        elif isinstance(type_, oer.Enumerated):
            return self._enumerated(type_, controller)
        elif isinstance(type_, oer.BitString):
            # noinspection PyTypeChecker
            return self._bitstring(type_, controller)
        elif isinstance(type_, oer.Null):
            return self._null(type_, controller)
        elif isinstance(type_, oer.Recursive):
            # noinspection PyUnresolvedReferences
            return self.create_view_and_controller(type_.inner, checker.inner, controller)
        else:
            return self._text(type_, f'ASN.1 type {type_.name} {type_.type_name} not supported')

    def _text(self, type_: oer.Type, text: str) -> AbstractView:
        return self._view_factory.get_text_view(type_.name, text)

    def _null(self, type_: oer.Type, controller: Controller) -> AbstractView:
        ControllerFactory(controller).create_null_controller(type_)
        return self._view_factory.get_text_view(type_.name, "NULL")

    def _number(self, type_: Union[oer.Integer, oer.Real], checker: constraints_checker.Type, controller: Controller) -> AbstractView:
        view, value_interface, optional_interface = self._view_factory.get_number_view(type_.name, type_.optional, self.__get_limit(checker.minimum),
                                                                                       self.__get_limit(checker.maximum), isinstance(type_, oer.Real))

        ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface, self.__get_limit(checker.minimum))

        return view

    def _sequence(self, type_: oer.Sequence, checker: constraints_checker.Dict, controller: Controller) -> AbstractView:
        view, optional_interface = self._view_factory.get_container_view(type_.name, type_.optional)

        sub_controller = ControllerFactory(controller).create_container_controller(type_, optional_interface)

        for sub_type in type_.root_members + ([] if type_.additions is None else type_.additions):
            view.add_child(self.create_view_and_controller(sub_type, self.__get_member_checker(checker, sub_type.name), sub_controller))

        return view

    def _sequence_of(self, type_: oer.SequenceOf, checker: constraints_checker.List, controller: Controller) -> AbstractView:
        view, value_interface, optional_interface = self._view_factory.get_list_view(type_.name, self.__get_limit(checker.minimum),
                                                                                     self.__get_limit(checker.maximum), type_.optional)

        list_instance_factory = ListInstanceFactory(self._view_factory, view, type_.element_type, checker.element_type)
        ControllerFactory(controller).create_list_controller(type_, value_interface, optional_interface, list_instance_factory,
                                                             self.__get_limit(checker.minimum))

        return view

    def _enumerated(self, type_: oer.Enumerated, controller: Controller) -> AbstractView:
        choices = [str(value) for value in type_.value_to_data.values()]
        view, value_interface, optional_interface = self._view_factory.get_enumerated_view(type_.name, choices, type_.optional)

        ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface)

        return view

    def _bool(self, type_: oer.Boolean, controller: Controller):
        view, value_interface, optional_interface = self._view_factory.get_boolean_view(type_.name, type_.optional)

        ControllerFactory(controller).create_bool_controller(type_, value_interface, optional_interface)

        return view

    def _string(self, type_: oer.VisibleString, checker: constraints_checker.String, controller: Controller):
        view, value_interface, optional_interface = self._view_factory.get_string_view(type_.name, type_.type_name, type_.optional,
                                                                                       self.__get_limit(checker.minimum), self.__get_limit(checker.maximum))

        ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface, self.__get_limit(checker.minimum))

        return view

    def _hex_string(self, type_: oer.OctetString, checker: constraints_checker.String, controller: Controller):
        view, value_interface, optional_interface = self._view_factory.get_hex_string_view(type_.name, type_.optional, self.__get_limit(checker.minimum),
                                                                                           self.__get_limit(checker.maximum))

        ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface, self.__get_limit(checker.minimum))

        return view

    def _bitstring(self, type_: oer.BitString, controller: Controller):
        if type_.number_of_bits is None:
            view, value_interface, optional_interface = self._view_factory.get_hex_string_view(type_.name, type_.optional, None, None)

            ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface, None)
        else:
            view, value_interface, optional_interface = self._view_factory.get_bitstring_view(type_.name, type_.number_of_bits, type_.named_bits,
                                                                                              type_.optional)

            ControllerFactory(controller).create_bitstring_controller(type_, value_interface, optional_interface)

        return view

    def _choice(self, type_: oer.Choice, checker: constraints_checker.Choice, controller: Controller):
        choices = [member.name for member in type_.members]
        view, value_interface, optional_interface = self._view_factory.get_choice_view(type_.name, choices, type_.optional)

        members = {member.name: member for member in type_.members}
        checkers = {member.name: member for member in checker.members}

        choice_instance_factory = ChoiceInstanceFactory(self._view_factory, view, members, checkers)
        ControllerFactory(controller).create_choice_controller(type_, value_interface, optional_interface, choice_instance_factory)

        return view

    @staticmethod
    def __get_member_checker(checker: constraints_checker.Dict, name: str) -> constraints_checker.Type:
        for member in checker.members:
            if member.name == name:
                return member

    @staticmethod
    def __get_limit(limit: Any):
        return None if limit in ['MIN', 'MAX'] else limit
