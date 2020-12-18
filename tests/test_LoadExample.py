import threading
from time import sleep
from unittest import TestCase

import wx

import asn1editor
from asn1editor.wxPython.ViewSelect import ViewType
from tests.TestPlugin import TestPlugin


def delay(main_window: asn1editor.wxPython.MainWindow):
    sleep(1)

    main_window.Close(True)
    wx.GetApp().ExitMainLoop()


class LoadExample(TestCase):
    @staticmethod
    def test_tree():
        LoadExample.__test_internal(ViewType.TREE)

    @staticmethod
    def test_group():
        LoadExample.__test_internal(ViewType.GROUPS)

    @staticmethod
    def __test_internal(v: ViewType):
        # noinspection PyUnusedLocal
        app = wx.App()
        main_window = asn1editor.wxPython.MainWindow(plugins=[TestPlugin()])
        main_window.select_view(v)

        test_types = [('example/example.asn', 'EXAMPLE.Sequence')]

        for spec, type_ in test_types:
            main_window.load_spec(spec, type_)
            action_thread = threading.Thread(target=delay, args=[main_window])
            action_thread.start()
            main_window.Show()
            app.MainLoop()
            action_thread.join(timeout=0.0)

        app.Destroy()
