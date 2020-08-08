import random
import threading
from time import sleep
from unittest import TestCase

import asn1tools
import wx

import asn1editor


def actions(main_window: asn1editor.wxPython.MainWindow):
    def get_children(window: wx.Window):
        my_children = window.GetChildren()
        if my_children is not None:
            their_children = []
            for my_child in my_children:
                their_children += get_children(my_child)
            return list(my_children) + their_children
        else:
            return []

    sleep(1)

    children = get_children(main_window)
    key_codes = [wx.WXK_TAB, wx.WXK_DOWN, wx.WXK_UP, wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_SPACE, wx.WXK_SELECT] + [c for c in range(ord('1'), ord('9'))]

    for i in range(10000):
        key_event = wx.KeyEvent(wx.EVT_CHAR.typeId)
        key_event.SetKeyCode(random.choice(key_codes))

        child = random.choice(children)
        event_handler = child.GetEventHandler()
        wx.PostEvent(event_handler, key_event)
    try:
        main_window.save_data_to_file('test.json')
    except asn1tools.ConstraintsError:
        pass

    main_window.Close(True)


class MonkeyTest(TestCase):
    def test_monkey(self):
        return
        # noinspection PyUnusedLocal
        app = wx.App()
        main_window = asn1editor.wxPython.MainWindow()

        test_types = [('example/example.asn', 'EXAMPLE.Sequence')]

        for spec, type_ in test_types:
            main_window.load_spec(spec, type_)
            action_thread = threading.Thread(target=actions, args=[main_window])
            action_thread.start()
            main_window.Show()
            app.MainLoop()
            action_thread.join(timeout=0.0)

        app.Destroy()
