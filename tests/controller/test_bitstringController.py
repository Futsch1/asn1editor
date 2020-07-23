import typing
from unittest import TestCase

from asn1editor.controller import Controller
from asn1editor.interfaces.BitstringInterface import BitstringInterface
from tests.controller.test_valueBoolControllers import TestOptionalInterface


class TestBitstringInterface(BitstringInterface):

    def __init__(self):
        self.values = []

    def get_values(self) -> typing.List[int]:
        return self.values

    def set_values(self, values: typing.List[int]):
        self.values = values


class TestBitstringController(TestCase):
    def test_add_controller(self):
        with self.assertRaises(Exception):
            root = Controller.RootController('root')
            controller = Controller.BitstringController('test', root, TestBitstringInterface(), None, 5)
            controller.add_controller('test', controller)

    def test_model_to_view(self):
        root = Controller.RootController('root')
        value_interface = TestBitstringInterface()
        optional_interface = TestOptionalInterface()

        controller = Controller.BitstringController('test', root, value_interface, None, 5)
        with self.assertRaises(AssertionError):
            controller.model_to_view({})

        controller = Controller.BitstringController('test', root, value_interface, optional_interface, 6)

        controller.model_to_view({})
        self.assertFalse(optional_interface.val)

        with self.assertRaises(AssertionError):
            controller.model_to_view({'test': (b'\x00', 7)})

        controller.model_to_view({'test': (b'\x33', 6)})
        self.assertListEqual(value_interface.values, [0, 1, 4, 5])

        controller = Controller.BitstringController('test', root, value_interface, optional_interface, 22)

        controller.model_to_view({'test': (b'\x82\x81\x81', 22)})
        self.assertListEqual(value_interface.values, [1, 7, 8, 15, 16])

    def test_view_to_model(self):
        root = Controller.RootController('root')
        value_interface = TestBitstringInterface()
        optional_interface = TestOptionalInterface()

        controller = Controller.BitstringController('test', root, value_interface, optional_interface, 22)

        optional_interface.val = False
        self.assertIsNone(controller.view_to_model())

        optional_interface.val = True
        self.assertEqual(controller.view_to_model(), (b'\x00\x00\x00', 22))

        value_interface.values = [1, 7, 8, 15, 16]
        self.assertEqual(controller.view_to_model(), (b'\x82\x81\x01', 22))
