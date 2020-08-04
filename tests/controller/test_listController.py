from unittest import TestCase

from asn1editor.controller import Controller, Converter
from tests.controller.test_valueBoolControllers import TestValueInterface, TestOptionalInterface


class TestListInstanceFactory:
    def __init__(self):
        self.values = {}
        self.instances = {}

    def create(self, i, p: Controller.ListController):
        self.values[i] = TestValueInterface()
        self.instances[i] = Controller.ValueController(str(i), p, self.values[i], None, Converter.Str(0, None))

    def destroy(self, i):
        del self.values[i]
        del self.instances[i]


class TestListController(TestCase):
    def test_init(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface = TestOptionalInterface()

        Controller.ListController('test', root, value_interface, None, TestListInstanceFactory(), 1)
        self.assertEqual(value_interface.val, '1')

        value_interface.val = 42
        Controller.ListController('test', root, value_interface, optional_interface, TestListInstanceFactory(), 0)
        self.assertEqual(value_interface.val, 42)

    def test_add_controller(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()

        controller = Controller.ListController('test', root, value_interface, None, TestListInstanceFactory(), 0)
        self.assertEqual(len(controller._controllers), 0)
        controller.add_controller('sub', controller)
        self.assertEqual(len(controller._controllers), 1)

    def test_model_to_view(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface = TestOptionalInterface()
        list_instance_factory = TestListInstanceFactory()

        controller = Controller.ListController('test', root, value_interface, None, list_instance_factory, 0)

        with self.assertRaises(AssertionError):
            controller.model_to_view({})

        controller = Controller.ListController('test', root, value_interface, optional_interface, list_instance_factory, 0)

        controller.model_to_view({})
        self.assertFalse(optional_interface.val)

        controller.model_to_view({'test': []})
        self.assertEqual(value_interface.val, '0')
        self.assertEqual(len(list_instance_factory.instances), 0)
        self.assertTrue(optional_interface.val)

        controller.model_to_view({'test': ['1', '2', '3']})
        self.assertEqual(value_interface.val, '3')
        self.assertEqual(len(list_instance_factory.instances), 3)
        self.assertTrue(optional_interface.val)
        self.assertEqual(list_instance_factory.values[0].val, '1')
        self.assertEqual(list_instance_factory.values[1].val, '2')
        self.assertEqual(list_instance_factory.values[2].val, '3')

    def test_view_to_model(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface = TestOptionalInterface()
        list_instance_factory = TestListInstanceFactory()

        controller = Controller.ListController('test', root, value_interface, optional_interface, list_instance_factory, 0)

        optional_interface.val = False
        self.assertIsNone(controller.view_to_model())

        optional_interface.val = True
        self.assertEqual(controller.view_to_model(), [])

        value_interface.val = 2
        controller.event_handler()
        list_instance_factory.values[0].val = 1
        list_instance_factory.values[1].val = 2
        self.assertEqual(controller.view_to_model(), [1, 2])

    def test_event_handlers(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface = TestOptionalInterface()
        list_instance_factory = TestListInstanceFactory()

        controller = Controller.ListController('test', root, value_interface, optional_interface, list_instance_factory, 0)
        self.assertEqual(len(list_instance_factory.instances), 0)

        value_interface.val = 2
        controller.event_handler()
        self.assertEqual(len(list_instance_factory.instances), 2)

        optional_interface.val = False
        controller.optional_handler()
        self.assertEqual(len(list_instance_factory.instances), 0)
        self.assertEqual(value_interface.val, 2)

        optional_interface.val = True
        controller.optional_handler()
        self.assertEqual(len(list_instance_factory.instances), 2)
        self.assertEqual(value_interface.val, 2)
