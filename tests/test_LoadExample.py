import json
import threading
from time import sleep
from unittest import TestCase

import wx

import asn1editor
from asn1editor.wxPython.ViewSelect import ViewType, TagInfo
from tests import TestHelper
from tests.TestPlugin import TestPlugin


def delay(main_window: asn1editor.wxPython.MainWindow):
    sleep(1)
    main_window.Close(True)
    wx.GetApp().ExitMainLoop()


class LoadExample(TestCase):

    def test_tree(self):
        self.__test_internal(ViewType.TREE, TagInfo.LABELS)

    def test_group(self):
        self.__test_internal(ViewType.GROUPS, TagInfo.TOOLTIPS)

    def __test_internal(self, v: ViewType, t: TagInfo):
        app = TestHelper.get_wx_app()
        # noinspection PyUnusedLocal
        main_window = asn1editor.wxPython.MainWindow(plugins=[TestPlugin()])

        self.assertTrue(main_window.load_spec('example/example.asn', 'EXAMPLE.Sequence'))
        main_window.load_data_from_file('example/example_with_additionals.json')
        main_window.save_data_to_file('test.json')
        with open('test.json', 'r') as f:
            test_content = json.load(f)
        with open('example/example_with_additionals.json', 'r') as f:
            example_content = json.load(f)
        self.assertEqual(test_content, example_content)

        main_window.select_view_and_tag_info(v, t)

        action_thread = threading.Thread(target=delay, args=[main_window])
        action_thread.start()
        main_window.Show()
        app.MainLoop()
        action_thread.join(timeout=0.0)
