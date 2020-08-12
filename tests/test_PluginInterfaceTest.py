import typing
from unittest import TestCase
from unittest.mock import patch

import wx

import asn1editor
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
            self.assertIsNone(plugin.plugin_interface.text_entry("Test my entry", "Default"))

        with patch('wx.SingleChoiceDialog') as SingleChoiceDialogMock:
            instance = SingleChoiceDialogMock.return_value
            instance.GetStringSelection.return_value = 'Test'
            instance.__enter__.return_value = instance

            instance.ShowModal.return_value = wx.ID_OK
            self.assertEqual('Test', plugin.plugin_interface.choice_entry("Test my entry", ["Test", "Test2"]))

            instance.ShowModal.return_value = wx.ID_CANCEL
            self.assertIsNone(plugin.plugin_interface.choice_entry("Test my entry", ["Test", "Test2"], "Test2"))

        with patch('wx.FileDialog') as FileDialogMock:
            instance = FileDialogMock.return_value
            instance.GetPaths.return_value = ['example/example.asn']
            instance.GetMessage.return_value = 'TestFile'
            instance.__enter__.return_value = instance

            instance.ShowModal.return_value = wx.ID_OK
            self.assertEqual('example/example.asn', plugin.plugin_interface.file_picker("Test my entry", "Test", True))

            instance.ShowModal.return_value = wx.ID_CANCEL
            self.assertIsNone(plugin.plugin_interface.file_picker("Test my entry", "Test", False))
            instance.SetPath.assert_called_once_with('example/')

        with patch('wx.DirDialog') as DirDialogMock:
            instance = DirDialogMock.return_value
            instance.GetPaths.return_value = ['example/example']
            instance.GetMessage.return_value = 'TestDir'
            instance.__enter__.return_value = instance

            instance.ShowModal.return_value = wx.ID_OK
            self.assertEqual('example/example', plugin.plugin_interface.dir_picker("Test my entry"))

            instance.ShowModal.return_value = wx.ID_CANCEL
            self.assertIsNone(plugin.plugin_interface.dir_picker("Test my entry"))
            instance.SetPath.assert_called_once_with('example/')

        plugin.plugin_interface.show_status("Test status bar")
        self.assertEqual(main_window._status_bar.GetStatusText(), 'Test status bar')

        with patch('wx.MessageBox') as MessageBox:
            plugin.plugin_interface.show_message('Test', asn1editor.PluginInterface.MessageType.ERROR)
            MessageBox.assert_called_once()

        with patch('wx.ProgressDialog') as ProgressDialog:
            instance = ProgressDialog.return_value
            instance.__enter__.return_value = instance

            plugin.plugin_interface.show_progress('Test', 100)
            ProgressDialog.assert_called_once()

            plugin.plugin_interface.update_progress(False, 3)
            instance.Update.assert_called_once_with(3)

            plugin.plugin_interface.update_progress(False)
            instance.Pulse.assert_called_once()

            plugin.plugin_interface.update_progress(True)
            instance.Close.assert_called_once()

        app.Destroy()

    def test_spec_interfaces(self):
        app = wx.App()
        plugin = TestPlugin()
        main_window = MainWindow(plugin)

        self.assertIsNone(plugin.plugin_interface.get_spec_filename())
        self.assertIsNone(plugin.plugin_interface.get_typename())

        main_window.load_spec('example/example.asn', 'EXAMPLE.Sequence')

        self.assertEqual(plugin.plugin_interface.get_spec_filename(), 'example/example.asn')
        self.assertEqual(plugin.plugin_interface.get_typename(), 'EXAMPLE.Sequence')

        app.Destroy()

    def test_encoding_decoding(self):
        app = wx.App()
        plugin = TestPlugin()
        main_window = MainWindow(plugin)

        main_window.load_spec('example/example.asn', 'EXAMPLE.Sequence')
        asn1spec = plugin.plugin_interface.get_spec('jer')
        self.assertIn('EXAMPLE', asn1spec.modules)

        jer_encoded = plugin.plugin_interface.encode_data('jer')
        plugin.plugin_interface.show_data(jer_encoded, 'jer')

        app.Destroy()

    def test_settings(self):
        app = wx.App()
        plugin = TestPlugin()
        main_window = MainWindow(plugin)

        plugin.plugin_interface.get_settings()['Test'] = 1

        main_window.close(wx.KeyEvent())

        main_window = MainWindow(plugin)

        self.assertEqual(plugin.plugin_interface.get_settings()['Test'], 1)
        plugin.plugin_interface.get_settings()['Test'] = 0

        main_window.close(wx.KeyEvent())

        main_window = MainWindow(plugin)

        self.assertEqual(plugin.plugin_interface.get_settings()['Test'], 0)

        main_window.close(wx.KeyEvent())
        app.Destroy()
