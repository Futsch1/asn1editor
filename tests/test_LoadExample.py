import threading
from time import sleep
from unittest import TestCase

import wx

import asn1editor
from asn1editor.wxPython.ViewSelect import ViewType
from tests import testHelper
from tests.TestPlugin import TestPlugin


def delay(main_window: asn1editor.wxPython.MainWindow):
    sleep(1)
    main_window.Close(True)
    wx.GetApp().ExitMainLoop()


class LoadExample(TestCase):

    def test_tree(self):
        self.__test_internal(ViewType.TREE)

    def test_group(self):
        self.__test_internal(ViewType.GROUPS)

    @staticmethod
    def __test_internal(v: ViewType):
        app = testHelper.get_wx_app()
        # noinspection PyUnusedLocal
        main_window = asn1editor.wxPython.MainWindow(plugins=[TestPlugin()])

        main_window.load_spec('example/example.asn', 'EXAMPLE.Sequence')
        main_window.select_view(v)

        action_thread = threading.Thread(target=delay, args=[main_window])
        action_thread.start()
        main_window.Show()
        app.MainLoop()
        action_thread.join(timeout=0.0)
