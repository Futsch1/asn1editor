import random
import threading
from time import sleep
from unittest import TestCase

import wx

import asn1editor


def actions(event_handler: wx.EvtHandler):
    sleep(1)
    for i in range(1000):
        key_event = wx.KeyEvent(wx.EVT_CHAR.typeId)
        key_event.SetKeyCode(random.choice([wx.WXK_TAB, wx.WXK_DOWN, wx.WXK_UP, wx.WXK_LEFT, wx.WXK_RIGHT]))
        wx.PostEvent(event_handler, key_event)


class MonkeyTest(TestCase):
    def test_monkey(self):
        return
        # noinspection PyUnusedLocal
        app = wx.App()
        main_window = asn1editor.wxPython.MainWindow()

        test_types = [('example/example.asn', 'EXAMPLE.Sequence')]

        for spec, type_ in test_types:
            main_window.load_spec(spec, type_)
            action_thread = threading.Thread(target=actions, args=[main_window.GetEventHandler()])
            action_thread.start()
            main_window.Show()
            app.MainLoop()
            main_window.save_data_to_file('test.json')
            action_thread.join(timeout=0.0)
