import typing
from typing import Callable
from unittest import TestCase

from asn1editor.controller import Controller, Converter
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface


class TestValueInterface(ValueInterface):
    def register_change_event(self, callback: typing.Callable):
        pass

    def __init__(self):
        self.val = ''

    def get_value(self) -> str:
        return self.val

    def set_value(self, val: str):
        self.val = val


class TestOptionalInterface(OptionalInterface):
    def register_optional_event(self, callback: Callable):
        pass

    def __init__(self):
        self.val = False

    def get_has_value(self) -> bool:
        return self.val

    def set_has_value(self, val: bool):
        self.val = val


class TestValueController(TestCase):
    def test_add_controller(self):
        with self.assertRaises(Exception):
            root = Controller.RootController('root')
            controller = Controller.ValueController('test', root, TestValueInterface(), None, Converter.Str(0, ''))
            controller.add_controller('test', controller)

    def test_init(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()

        Controller.ValueController('test', root, value_interface, None, Converter.Str(0, 'default'))
        self.assertEqual(value_interface.val, 'default')

        Controller.ValueController('test', root, value_interface, None, Converter.Int(0, 12))
        self.assertEqual(value_interface.val, '12')

        Controller.ValueController('test', root, value_interface, None, Converter.Int(0, None))
        self.assertEqual(value_interface.val, '0')

        Controller.ValueController('test', root, value_interface, None, Converter.Int(12, None))
        self.assertEqual(value_interface.val, '12')

    def test_model_to_view(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface = TestOptionalInterface()

        controller = Controller.ValueController('test', root, value_interface, None, Converter.Str(0, 'default'))
        controller.model_to_view({'test': 'new'})
        self.assertEqual(value_interface.val, 'new')

        controller.model_to_view('new2')
        self.assertEqual(value_interface.val, 'new2')

        with self.assertRaises(AssertionError):
            controller.model_to_view({})

        controller = Controller.ValueController('test', root, value_interface, optional_interface, Converter.Str(0, 'default'))
        controller.model_to_view({'test': 'new'})
        self.assertEqual(value_interface.val, 'new')
        self.assertTrue(optional_interface.val)

        controller.model_to_view({})
        self.assertFalse(optional_interface.val)

    def test_view_to_model(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface = TestOptionalInterface()

        controller = Controller.ValueController('test', root, value_interface, optional_interface, Converter.Str(0, 'default'))
        value_interface.val = 'new'
        optional_interface.val = True
        self.assertEqual('new', controller.view_to_model())

        optional_interface.val = False
        self.assertIsNone(controller.view_to_model())


class TestBoolController(TestCase):
    def test_add_controller(self):
        with self.assertRaises(Exception):
            root = Controller.RootController('root')
            controller = Controller.BoolController('test', root, TestValueInterface(), None, True)
            controller.add_controller('test', controller)

    def test_init(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()

        Controller.BoolController('test', root, value_interface, None, True)
        self.assertTrue(value_interface.val)

        Controller.BoolController('test', root, value_interface, None, False)
        self.assertFalse(value_interface.val)

    def test_model_to_view(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface = TestOptionalInterface()

        controller = Controller.BoolController('test', root, value_interface, None, True)
        controller.model_to_view({'test': 'false'})
        self.assertEqual(value_interface.val, 'false')

        controller.model_to_view('True')
        self.assertEqual(value_interface.val, 'True')

        with self.assertRaises(AssertionError):
            controller.model_to_view({})

        controller = Controller.BoolController('test', root, value_interface, optional_interface, True)
        controller.model_to_view({'test': 'false'})
        self.assertEqual(value_interface.val, 'false')
        self.assertTrue(optional_interface.val)

        controller.model_to_view({})
        self.assertFalse(optional_interface.val)

    def test_view_to_model(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface = TestOptionalInterface()

        controller = Controller.BoolController('test', root, value_interface, optional_interface, False)
        value_interface.val = 'True'
        optional_interface.val = True
        self.assertTrue(controller.view_to_model())

        optional_interface.val = False
        self.assertIsNone(controller.view_to_model())
