import typing
from unittest.mock import patch

import wx

import asn1editor
from unittest import TestCase

from asn1editor.wxPython.MainWindow import MainWindow


class TestPlugin(asn1editor.Plugin):
    def __init__(self):
        self.plugin_interface: typing.Optional[asn1editor.PluginInterface] = None
        self.name = "Test"
        self.menus = []

    def get_name(self) -> str:
        return self.name

    def get_menus(self) -> typing.List[typing.Tuple[str, typing.Callable]]:
        return self.menus

    def connect(self, plugin_interface: asn1editor.PluginInterface):
        self.plugin_interface = plugin_interface


class PluginInterfaceTest(TestCase):
    def test_dialogs(self):
        app = wx.App()
        plugin = TestPlugin()
        main_window = MainWindow(plugin)
        with patch('wx.TextEntryDialog') as TextEntryDialogMock:
            instance = TextEntryDialogMock.return_value
            instance.GetValue.return_value = 'Test'
            instance.__enter__.return_value = instance

            instance.ShowModal.return_value = wx.ID_OK
            self.assertEqual('Test', plugin.plugin_interface.text_entry("Test my entry"))

            instance.ShowModal.return_value = wx.ID_CANCEL
            self.assertIsNone(plugin.plugin_interface.text_entry("Test my entry"))

        with patch('wx.SingleChoiceDialog') as SingleChoiceDialogMock:
            instance = SingleChoiceDialogMock.return_value
            instance.GetStringSelection.return_value = 'Test'
            instance.__enter__.return_value = instance

            instance.ShowModal.return_value = wx.ID_OK
            self.assertEqual('Test', plugin.plugin_interface.choice_entry("Test my entry", ["Test", "Test2"]))

            instance.ShowModal.return_value = wx.ID_CANCEL
            self.assertIsNone(plugin.plugin_interface.choice_entry("Test my entry", ["Test", "Test2"]))

        with patch('wx.FileDialog') as FileDialogMock:
            instance = FileDialogMock.return_value
            instance.GetPath.return_value = 'Test'
            instance.__enter__.return_value = instance

            instance.ShowModal.return_value = wx.ID_OK
            self.assertEqual('Test', plugin.plugin_interface.file_picker("Test my entry", "Test", True))

            instance.ShowModal.return_value = wx.ID_CANCEL
            self.assertIsNone(plugin.plugin_interface.file_picker("Test my entry", "Test", False))

        with patch('wx.DirDialog') as DirDialogMock:
            instance = DirDialogMock.return_value
            instance.GetPath.return_value = 'Test'
            instance.__enter__.return_value = instance

            instance.ShowModal.return_value = wx.ID_OK
            self.assertEqual('Test', plugin.plugin_interface.dir_picker("Test my entry"))

            instance.ShowModal.return_value = wx.ID_CANCEL
            self.assertIsNone(plugin.plugin_interface.dir_picker("Test my entry"))

        plugin.plugin_interface.show_status("Test status bar")
        self.assertEqual(main_window._status_bar.GetStatusText(), 'Test status bar')

        app.Destroy()

    def test_spec_interfaces(self):
        app = wx.App()
        plugin = TestPlugin()
        main_window = MainWindow(plugin)

        self.assertIsNone(plugin.plugin_interface.get_spec_filename())
        self.assertIsNone(plugin.plugin_interface.get_typename())

        main_window.load_spec('../example/example.asn', 'EXAMPLE.Sequence')

        self.assertEqual(plugin.plugin_interface.get_spec_filename(), '../example/example.asn')
        self.assertEqual(plugin.plugin_interface.get_typename(), 'EXAMPLE.Sequence')

        app.Destroy()

    def test_encoding_decoding(self):
        app = wx.App()
        plugin = TestPlugin()
        main_window = MainWindow(plugin)

        main_window.load_spec('../example/example.asn', 'EXAMPLE.Sequence')
        asn1spec = plugin.plugin_interface.get_spec('jer')
        self.assertIn('EXAMPLE', asn1spec.modules)

        jer_encoded = plugin.plugin_interface.encode_data('jer')
        plugin.plugin_interface.show_data(jer_encoded, 'jer')

        app.Destroy()
