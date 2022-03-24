import typing

from asn1tools.codecs import constraints_checker
from asn1tools.compiler import oer

from asn1editor.TypeAugmenter import TypeAugmenter
from asn1editor.controller.ChoiceInstanceFactory import ChoiceInstanceFactory
from asn1editor.controller.Controller import Controller, RootController
from asn1editor.controller.ControllerFactory import ControllerFactory
from asn1editor.controller.ListInstanceFactory import ListInstanceFactory
from asn1editor.view.AbstractView import AbstractView
from asn1editor.view.AbstractViewFactory import AbstractViewFactory, TypeInfo


class ViewControllerFactory(object):
    def __init__(self, view_factory: AbstractViewFactory, type_augmenter: typing.Optional[TypeAugmenter]):
        self._view_factory = view_factory
        self._type_augmenter = type_augmenter

    def create(self, asn1_type: oer.CompiledType) -> typing.Tuple[AbstractView, Controller]:
        controller = RootController('root')
        view = self.create_view_and_controller(asn1_type.type, asn1_type.constraints_checker.type, controller)

        return view, controller

    def create_view_and_controller(self, type_: oer.Type, checker: constraints_checker.Type, controller: Controller) -> AbstractView:
        if isinstance(type_, oer.Integer) or isinstance(type_, oer.Real):
            view = self._number(type_, checker, controller)
        elif isinstance(type_, oer.Boolean):
            view = self._bool(type_, controller)
        elif isinstance(type_, oer.Sequence) or isinstance(type_, oer.Set):
            # noinspection PyTypeChecker
            view = self._sequence(type_, checker, controller)
        elif isinstance(type_, oer.SequenceOf) or isinstance(type_, oer.SetOf):
            # noinspection PyTypeChecker
            view = self._sequence_of(type_, checker, controller)
        elif isinstance(type_, oer.Choice):
            # noinspection PyTypeChecker
            view = self._choice(type_, checker, controller)
        elif isinstance(type_, oer.OctetString):
            # noinspection PyTypeChecker
            view = self._hex_string(type_, checker, controller)
        elif type(type_) in [oer.UTF8String, oer.VisibleString, oer.GeneralString, oer.IA5String, oer.ObjectIdentifier]:
            # noinspection PyTypeChecker
            view = self._string(type_, checker, controller)
        elif isinstance(type_, oer.Enumerated):
            view = self._enumerated(type_, controller)
        elif isinstance(type_, oer.BitString):
            # noinspection PyTypeChecker
            view = self._bitstring(type_, controller)
        elif isinstance(type_, oer.Null):
            view = self._null(type_, controller)
        elif isinstance(type_, oer.Recursive):
            # noinspection PyUnresolvedReferences
            view = self.create_view_and_controller(type_.inner, checker.inner, controller)
        elif isinstance(type_, oer.Date):
            view = self._date(type_, controller)
        elif isinstance(type_, oer.TimeOfDay):
            view = self._time(type_, controller)
        elif isinstance(type_, oer.DateTime) or isinstance(type_, oer.UTCTime) or isinstance(type_, oer.GeneralizedTime):
            view = self._datetime(type_, controller)
        else:
            view = self._text(type_, f'ASN.1 type {type_.name} {type_.type_name} not supported')

        return view

    def _text(self, type_: oer.Type, text: str) -> AbstractView:
        return self._view_factory.get_text_view(self.__get_type_info(type_, '?'), text)

    def _null(self, type_: oer.Type, controller: Controller) -> AbstractView:
        ControllerFactory(controller).create_null_controller(type_)
        return self._view_factory.get_text_view(self.__get_type_info(type_, controller.get_path()), "NULL")

    def _number(self, type_: typing.Union[oer.Integer, oer.Real], checker: constraints_checker.Type, controller: Controller) -> AbstractView:
        view, value_interface, optional_interface = self._view_factory.get_number_view(self.__get_type_info(type_, controller.get_path()),
                                                                                       self.__get_limit(checker.minimum), self.__get_limit(checker.maximum),
                                                                                       isinstance(type_, oer.Real))

        ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface, self.__get_limit(checker.minimum))

        return view

    def _sequence(self, type_: oer.Sequence, checker: constraints_checker.Dict, controller: Controller) -> AbstractView:
        view, optional_interface = self._view_factory.get_container_view(self.__get_type_info(type_, controller.get_path()))

        sub_controller = ControllerFactory(controller).create_container_controller(type_, optional_interface)

        # Additions are always optional
        additions = [] if type_.additions is None else type_.additions
        for sub_type in additions:
            sub_type.additional = True

        for sub_type in type_.root_members + additions:
            view.add_child(self.create_view_and_controller(sub_type, self.__get_member_checker(checker, sub_type.name), sub_controller))

        return view

    def _sequence_of(self, type_: oer.SequenceOf, checker: constraints_checker.List, controller: Controller) -> AbstractView:
        view, value_interface, optional_interface = self._view_factory.get_list_view(self.__get_type_info(type_, controller.get_path()),
                                                                                     self.__get_limit(checker.minimum),
                                                                                     self.__get_limit(checker.maximum))

        list_instance_factory = ListInstanceFactory(self._view_factory, self._type_augmenter, view, type_.element_type, checker.element_type)
        ControllerFactory(controller).create_list_controller(type_, value_interface, optional_interface, list_instance_factory,
                                                             self.__get_limit(checker.minimum))

        return view

    def _enumerated(self, type_: oer.Enumerated, controller: Controller) -> AbstractView:
        choices = [str(value) for value in type_.value_to_data.values()]
        view, value_interface, optional_interface = self._view_factory.get_enumerated_view(self.__get_type_info(type_, controller.get_path()), choices)

        ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface)

        return view

    def _bool(self, type_: oer.Boolean, controller: Controller):
        view, value_interface, optional_interface = self._view_factory.get_boolean_view(self.__get_type_info(type_, controller.get_path()))

        ControllerFactory(controller).create_bool_controller(type_, value_interface, optional_interface)

        return view

    def _string(self, type_: oer.VisibleString, checker: constraints_checker.String, controller: Controller):
        view, value_interface, optional_interface = self._view_factory.get_string_view(self.__get_type_info(type_, controller.get_path()),
                                                                                       self.__get_limit(checker.minimum), self.__get_limit(checker.maximum))

        ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface, self.__get_limit(checker.minimum))

        return view

    def _hex_string(self, type_: oer.OctetString, checker: constraints_checker.String, controller: Controller):
        view, value_interface, optional_interface = self._view_factory.get_hex_string_view(self.__get_type_info(type_, controller.get_path()),
                                                                                           self.__get_limit(checker.minimum), self.__get_limit(checker.maximum))

        ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface, self.__get_limit(checker.minimum))

        return view

    def _bitstring(self, type_: oer.BitString, controller: Controller):
        if type_.number_of_bits is None:
            view, value_interface, optional_interface = self._view_factory.get_hex_string_view(self.__get_type_info(type_, controller.get_path()), None, None)

            ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface, None)
        else:
            view, value_interface, optional_interface = self._view_factory.get_bitstring_view(self.__get_type_info(type_, controller.get_path()),
                                                                                              type_.number_of_bits, type_.named_bits)

            ControllerFactory(controller).create_bitstring_controller(type_, value_interface, optional_interface)

        return view

    def _choice(self, type_: oer.Choice, checker: constraints_checker.Choice, controller: Controller):
        choices = [member.name for member in type_.members]
        view, value_interface, optional_interface = self._view_factory.get_choice_view(self.__get_type_info(type_, controller.get_path()), choices)

        members = {member.name: member for member in type_.members}
        checkers = {member.name: member for member in checker.members}

        choice_instance_factory = ChoiceInstanceFactory(self._view_factory, self._type_augmenter, view, members, checkers)
        ControllerFactory(controller).create_choice_controller(type_, value_interface, optional_interface, choice_instance_factory)

        return view

    def _date(self, type_: oer.Date, controller: Controller):
        view, value_interface, optional_interface = self._view_factory.get_date_view(self.__get_type_info(type_, controller.get_path()))

        ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface)

        return view

    def _time(self, type_: oer.TimeOfDay, controller: Controller):
        view, value_interface, optional_interface = self._view_factory.get_time_view(self.__get_type_info(type_, controller.get_path()))

        ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface)

        return view

    def _datetime(self, type_: typing.Union[oer.DateTime, oer.UTCTime, oer.GeneralizedTime], controller: Controller):
        view, value_interface, optional_interface = self._view_factory.get_datetime_view(self.__get_type_info(type_, controller.get_path()))

        ControllerFactory(controller).create_value_controller(type_, value_interface, optional_interface)

        return view

    @staticmethod
    def __get_member_checker(checker: constraints_checker.Dict, name: str) -> constraints_checker.Type:
        for member in checker.members:
            if member.name == name:
                return member

    @staticmethod
    def __get_limit(limit: typing.Any) -> typing.Optional[int]:
        return None if limit in ['MIN', 'MAX'] or not isinstance(limit, int) else limit

    def __get_type_info(self, type_: oer.Type, path: str) -> TypeInfo:
        type_info = TypeInfo()
        type_info.name = type_.name
        type_info.optional = type_.optional
        type_info.additional = hasattr(type_, "additional")
        type_info.tag = f'0x{type_.tag.hex()}' if type_.tag is not None else ''
        if self._type_augmenter:
            if len(path):
                path += '.'
            path += f'{type_.name}'
            type_info.style = self._type_augmenter.get_style(path)
            type_info.help = self._type_augmenter.get_help(path)
        type_to_str = {oer.Integer: 'INTEGER', oer.Real: 'REAL', oer.Enumerated: 'ENUMERATED', oer.Boolean: 'BOOLEAN', oer.OctetString: 'OCTET STRING',
                       oer.VisibleString: 'VisibleString', oer.UTF8String: 'UTF8String', oer.GeneralString: 'GeneralString', oer.IA5String: 'IA5String',
                       oer.ObjectIdentifier: 'OBJECT IDENTIFIER', oer.BitString: 'BIT STRING', oer.Sequence: 'SEQUENCE', oer.Set: 'SET',
                       oer.SequenceOf: 'SEQUENCE OF', oer.SetOf: 'SET OF', oer.Choice: 'CHOICE', oer.Date: 'DATE', oer.TimeOfDay: 'TIME-OF-DAY',
                       oer.DateTime: 'DATE-TIME', oer.GeneralizedTime: 'GeneralizedTime', oer.UTCTime: 'UTCTime', oer.Null: 'NULL'}

        type_info.typename = type_to_str.get(type(type_), 'UNSUPPORTED: ' + str(type_))

        return type_info
