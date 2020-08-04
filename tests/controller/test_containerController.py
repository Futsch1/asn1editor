from unittest import TestCase

from asn1editor.controller import Controller
from asn1editor.controller import Converter
from tests.controller.test_listController import TestListInstanceFactory
from tests.controller.test_valueBoolControllers import TestValueInterface, TestOptionalInterface


class TestContainerController(TestCase):
    def test_add_controller(self):
        root = Controller.RootController('root')

        controller = Controller.ContainerController('test', root, None)
        self.assertEqual(len(controller._controllers), 0)
        controller.add_controller('sub', controller)
        self.assertEqual(len(controller._controllers), 1)

    def test_model_to_view_value(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface_container = TestOptionalInterface()
        optional_interface_value = TestOptionalInterface()

        container = Controller.ContainerController('test', root, None)
        Controller.ValueController('test', container, value_interface, None, Converter.Str(0, 'default'))
        container.model_to_view({'test': {'test': 'test'}})
        self.assertEqual(value_interface.val, 'test')

        container = Controller.ContainerController('test', root, optional_interface_container)
        Controller.ValueController('test', container, value_interface, optional_interface_value, Converter.Str(0, 'default'))
        container.model_to_view({'test': {'test': 'test'}})
        self.assertTrue(optional_interface_container.val)
        self.assertTrue(optional_interface_value.val)

        container.model_to_view({'test': {}})
        self.assertTrue(optional_interface_container.val)
        self.assertFalse(optional_interface_value.val)

        container.model_to_view({})
        self.assertFalse(optional_interface_container.val)

        container = Controller.ContainerController('test', root, None)
        container2 = Controller.ContainerController('test2', container, None)
        Controller.ValueController('test', container2, value_interface, None, Converter.Str(0, 'default'))
        container.model_to_view({'test': {'test2': {'test': 'test'}}})
        self.assertEqual(value_interface.val, 'test')

    def test_model_to_view_list(self):
        root = Controller.RootController('root')
        list_value_interface = TestValueInterface()
        value_interface = TestValueInterface()
        list_instance_factory = TestListInstanceFactory()

        container = Controller.ContainerController('test', root, None)
        Controller.ListController('test_list', container, list_value_interface, None, list_instance_factory, 0)

        container.model_to_view({'test': {'test_list': []}})
        self.assertEqual(list_value_interface.val, '0')
        self.assertEqual(len(list_instance_factory.instances), 0)

        container.model_to_view({'test': {'test_list': [1]}})
        self.assertEqual(list_value_interface.val, '1')
        self.assertEqual(len(list_instance_factory.instances), 1)
        self.assertEqual(list_instance_factory.values[0].val, 1)

        Controller.ValueController('test_val', container, value_interface, None, Converter.Str(0, 'default'))
        container.model_to_view({'test': {'test_list': [1], 'test_val': 'test'}})
        self.assertEqual(value_interface.val, 'test')

    def test_view_to_model_value(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface_container = TestOptionalInterface()
        optional_interface_value = TestOptionalInterface()

        container = Controller.ContainerController('test', root, None)
        Controller.ValueController('test', container, value_interface, None, Converter.Str(0, 'default'))
        value_interface.val = 'test'

        self.assertEqual(container.view_to_model(), {'test': 'test'})

        container = Controller.ContainerController('test', root, optional_interface_container)
        Controller.ValueController('test', container, value_interface, optional_interface_value, Converter.Str(0, 'default'))

        optional_interface_value.val = True
        optional_interface_container.val = True
        self.assertEqual(container.view_to_model(), {'test': 'default'})

        optional_interface_value.val = False
        optional_interface_container.val = False
        self.assertIsNone(container.view_to_model())

        optional_interface_value.val = False
        optional_interface_container.val = True
        self.assertEqual(container.view_to_model(), {})

        container = Controller.ContainerController('test', root, None)
        container2 = Controller.ContainerController('test2', container, None)
        Controller.ValueController('test', container2, value_interface, None, Converter.Str(0, 'default'))

        value_interface.val = 'test'
        self.assertEqual(container.view_to_model(), {'test2': {'test': 'test'}})

    def test_view_to_model_list(self):
        root = Controller.RootController('root')
        list_value_interface = TestValueInterface()
        value_interface = TestValueInterface()
        list_instance_factory = TestListInstanceFactory()

        container = Controller.ContainerController('test', root, None)
        list_controller = Controller.ListController('test_list', container, list_value_interface, None, list_instance_factory, 0)

        self.assertEqual(container.view_to_model(), {'test_list': []})

        list_value_interface.val = 1
        list_controller.event_handler()
        list_instance_factory.values[0].val = 1

        self.assertEqual(container.view_to_model(), {'test_list': [1]})

        container.model_to_view({'test': {'test_list': [1]}})
        self.assertEqual(list_value_interface.val, '1')
        self.assertEqual(len(list_instance_factory.instances), 1)
        self.assertEqual(list_instance_factory.values[0].val, 1)

        Controller.ValueController('test_val', container, value_interface, None, Converter.Str(0, 'default'))
        value_interface.val = 'test'
        self.assertEqual(container.view_to_model(), {'test_list': [1], 'test_val': 'test'})
