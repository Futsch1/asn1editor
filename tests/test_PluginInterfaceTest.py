import typing
from unittest import TestCase
from unittest.mock import patch

import wx

import asn1editor
from asn1editor.wxPython.MainWindow import MainWindow
from tests import TestHelper


class TestPlugin(asn1editor.Plugin):
    def __init__(self):
        self.plugin_interface: typing.Optional[asn1editor.PluginInterface] = None
        self.name = "Test"
        self.menus = []
        self.tools = []

    def get_name(self) -> str:
        return self.name

    def get_menus(self) -> typing.List[typing.Tuple[str, typing.Callable]]:
        return self.menus

    def get_tools(self) -> typing.List[typing.Tuple[str, str, str, typing.Callable]]:
        return self.tools

    def get_about(self) -> typing.Optional[str]:
        return None

    def connect(self, plugin_interface: asn1editor.PluginInterface):
        self.plugin_interface = plugin_interface


class PluginInterfaceTest(TestCase):
    def test_dialogs(self):
        app = TestHelper.get_wx_app()

        plugin = TestPlugin()
        main_window = MainWindow([plugin], enable_load_last=False)
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
            self.assertEqual('Test', plugin.plugin_interface.choice_entry("Test my entry", "Test caption", ["Test", "Test2"], "Test2"))

            instance.ShowModal.return_value = wx.ID_CANCEL
            self.assertIsNone(plugin.plugin_interface.choice_entry("Test my entry", "Test caption", ["Test", "Test2"], "NotThere"))

        with patch('wx.FileDialog') as FileDialogMock:
            instance = FileDialogMock.return_value
            instance.GetPaths.return_value = ['example2/example.asn']
            instance.GetMessage.return_value = 'TestFile'
            instance.__enter__.return_value = instance

            instance.ShowModal.return_value = wx.ID_OK
            self.assertEqual('example2/example.asn', plugin.plugin_interface.file_picker("Test my entry", "Test", True))

            instance.SetDirectory.reset_mock()
            instance.ShowModal.return_value = wx.ID_CANCEL
            self.assertIsNone(plugin.plugin_interface.file_picker("Test my entry", "Test", False))
            instance.SetDirectory.assert_called_once_with('example2/')

        with patch('wx.DirDialog') as DirDialogMock:
            instance = DirDialogMock.return_value
            instance.GetPaths.return_value = ['example3/example']
            instance.GetMessage.return_value = 'TestDir'
            instance.__enter__.return_value = instance

            instance.ShowModal.return_value = wx.ID_OK
            self.assertEqual('example3/example', plugin.plugin_interface.dir_picker("Test my entry"))

            instance.SetPath.reset_mock()
            instance.ShowModal.return_value = wx.ID_CANCEL
            self.assertIsNone(plugin.plugin_interface.dir_picker("Test my entry"))
            instance.SetPath.assert_called_once_with('example3/')

        plugin.plugin_interface.show_status("Test status bar")
        self.assertEqual(main_window._status_bar.GetStatusText(), 'Test status bar')

        with patch('wx.MessageBox') as MessageBox:
            plugin.plugin_interface.show_message('Test', "Test caption", asn1editor.PluginInterface.MessageType.ERROR)
            MessageBox.assert_called_once()

        with patch('wx.MessageBox') as MessageBox:
            MessageBox.return_value = wx.YES
            self.assertTrue(plugin.plugin_interface.show_message('Question', "Test caption", asn1editor.PluginInterface.MessageType.QUESTION))

            MessageBox.return_value = wx.NO
            self.assertFalse(plugin.plugin_interface.show_message('Question', "Test caption", asn1editor.PluginInterface.MessageType.QUESTION))

        with patch('wx.ProgressDialog') as ProgressDialog:
            instance = ProgressDialog.return_value
            instance.__enter__.return_value = instance
            instance.Update.return_value = (True, False)
            instance.Pulse.return_value = (False, True)

            plugin.plugin_interface.show_progress('Test', "Test caption", 100)
            ProgressDialog.assert_called_once()

            self.assertTrue(plugin.plugin_interface.update_progress(None, False, 3))
            instance.Update.assert_called_once_with(3, newmsg=None)

            self.assertFalse(plugin.plugin_interface.update_progress(None, False))
            instance.Pulse.assert_called_once()

            plugin.plugin_interface.update_progress(None, True)
            instance.Close.assert_called_once()

        app.GetTopWindow().Close()

    def test_multiple_plugins(self):
        app = TestHelper.get_wx_app()

        plugin1 = TestPlugin()
        plugin2 = TestPlugin()
        MainWindow([plugin1, plugin2], enable_load_last=False)
        with patch('wx.TextEntryDialog') as TextEntryDialogMock:
            instance = TextEntryDialogMock.return_value
            instance.GetValue.return_value = 'Test'
            instance.__enter__.return_value = instance

            instance.ShowModal.return_value = wx.ID_OK
            self.assertEqual('Test', plugin2.plugin_interface.text_entry("Test my entry"))

            self.assertEqual('Test', plugin1.plugin_interface.text_entry("Test my entry"))

        app.GetTopWindow().Close()

    def test_spec_interfaces(self):
        app = TestHelper.get_wx_app()

        plugin = TestPlugin()
        main_window = MainWindow([plugin], enable_load_last=False)

        self.assertIsNone(plugin.plugin_interface.get_spec_filename())
        self.assertIsNone(plugin.plugin_interface.get_typename())

        self.assertTrue(main_window.load_spec('example/example.asn', 'EXAMPLE.Sequence'))

        self.assertEqual(plugin.plugin_interface.get_spec_filename(), 'example/example.asn')
        self.assertEqual(plugin.plugin_interface.get_typename(), 'EXAMPLE.Sequence')

        app.GetTopWindow().Close()

    def test_encoding_decoding(self):
        app = TestHelper.get_wx_app()

        plugin = TestPlugin()
        main_window = MainWindow([plugin], enable_load_last=False)

        self.assertTrue(main_window.load_spec('example/example.asn', 'EXAMPLE.Sequence'))
        asn1spec = plugin.plugin_interface.get_spec('jer')
        self.assertIn('EXAMPLE', asn1spec.modules)

        jer_encoded = plugin.plugin_interface.encode_data('jer')
        plugin.plugin_interface.show_data(jer_encoded, 'jer')

        app.GetTopWindow().Close()

    def test_settings(self):
        app = TestHelper.get_wx_app()

        plugin = TestPlugin()
        MainWindow([plugin], enable_load_last=False)

        plugin.plugin_interface.get_settings()['Test'] = 1

        app.GetTopWindow().Close()

        MainWindow([plugin], enable_load_last=False)

        self.assertEqual(plugin.plugin_interface.get_settings()['Test'], 1)
        plugin.plugin_interface.get_settings()['Test'] = 0

        app.GetTopWindow().Close()

        MainWindow([plugin], enable_load_last=False)

        self.assertEqual(plugin.plugin_interface.get_settings()['Test'], 0)

        app.GetTopWindow().Close()
