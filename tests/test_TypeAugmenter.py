from unittest import TestCase
from unittest.mock import MagicMock

from asn1editor.wxPython.MainWindow import MainWindow
from tests import TestHelper


class TypeAugmenterTest(TestCase):
    def test_augmenter(self):
        # noinspection PyUnusedLocal
        app = TestHelper.get_wx_app()

        type_augmenter = MagicMock()
        main_window = MainWindow(type_augmenter=type_augmenter)

        self.assertTrue(main_window.load_spec('example/example.asn', 'EXAMPLE.Sequence'))

        type_augmenter.set_spec_filename.assert_called_with('example/example.asn')
        type_augmenter.get_help.assert_any_call('Sequence.choiceExample.exampleList')
        type_augmenter.get_help.assert_any_call('Sequence.example1.member1')
        type_augmenter.get_style.assert_any_call('Sequence.choiceExample.exampleList')
        type_augmenter.get_style.assert_any_call('Sequence.example1.member1')
