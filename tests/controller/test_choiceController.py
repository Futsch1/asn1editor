from unittest import TestCase

from asn1editor.controller import Controller, Converter
from tests.controller.test_valueBoolControllers import TestValueInterface, TestOptionalInterface


class TestChoiceInstanceFactory:
    def __init__(self):
        self.value = None
        self.instance = None
        self.member = None

    def create(self, member: str, p: Controller.ListController):
        self.member = member
        self.value = TestValueInterface()
        self.instance = Controller.ValueController(member, p, self.value, None, Converter.Str(0, None))


class TestListController(TestCase):
    def test_init(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()

        Controller.ChoiceController('test', root, value_interface, None, TestChoiceInstanceFactory(), 'choice')
        self.assertEqual(value_interface.val, 'choice')

    def test_add_controller(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()

        controller = Controller.ChoiceController('test', root, value_interface, None, TestChoiceInstanceFactory(), 'choice')
        controller.add_controller('sub', controller)
        self.assertEqual(controller._controller, controller)

    def test_model_to_view(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface = TestOptionalInterface()
        choice_instance_factory = TestChoiceInstanceFactory()

        controller = Controller.ChoiceController('test', root, value_interface, None, choice_instance_factory, 'choice')

        with self.assertRaises(AssertionError):
            controller.model_to_view({})

        controller = Controller.ChoiceController('test', root, value_interface, optional_interface, choice_instance_factory, 'choice')

        controller.model_to_view({})
        self.assertFalse(optional_interface.val)

        controller.model_to_view({'test': ('choice2', '2')})
        self.assertEqual(value_interface.val, 'choice2')
        self.assertEqual(choice_instance_factory.member, 'choice2')
        self.assertTrue(optional_interface.val)
        self.assertEqual(choice_instance_factory.value.val, '2')

    def test_view_to_model(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface = TestOptionalInterface()
        choice_instance_factory = TestChoiceInstanceFactory()

        controller = Controller.ChoiceController('test', root, value_interface, optional_interface, choice_instance_factory, 'choice')

        optional_interface.val = False
        self.assertIsNone(controller.view_to_model())

        optional_interface.val = True
        choice_instance_factory.value.val = '1'
        self.assertEqual(controller.view_to_model(), ('choice', '1'))

        optional_interface.val = True
        value_interface.val = 'choice2'
        choice_instance_factory.value.val = '2'
        self.assertEqual(controller.view_to_model(), ('choice2', '2'))

    def test_event_handlers(self):
        root = Controller.RootController('root')
        value_interface = TestValueInterface()
        optional_interface = TestOptionalInterface()
        choice_instance_factory = TestChoiceInstanceFactory()

        controller = Controller.ChoiceController('test', root, value_interface, optional_interface, choice_instance_factory, 'choice')

        value_interface.val = 'choice2'
        controller.event_handler()
        self.assertEqual(choice_instance_factory.member, 'choice2')
