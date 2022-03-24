from unittest import TestCase

from asn1editor.controller import Controller


class TestValueController(TestCase):
    def test_controller(self):
        root = Controller.RootController('root')

        controller = Controller.Controller('Test', root, None)

        with self.assertRaises(NotImplementedError):
            controller.add_controller('Error', root)

        with self.assertRaises(NotImplementedError):
            controller.model_to_view({})

        with self.assertRaises(NotImplementedError):
            controller.view_to_model()

        controller.optional_handler()

        self.assertEqual(str(controller), 'Test')

    def test_nullController(self):
        root = Controller.RootController('root')

        controller = Controller.NullController('Test', root, None)

        with self.assertRaises(Exception):
            controller.add_controller('Test', root)
