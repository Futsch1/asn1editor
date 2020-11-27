import os
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

    main_window.SetFocus()

    key_codes = [wx.WXK_TAB, wx.WXK_DOWN, wx.WXK_UP, wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_SPACE] + [c for c in range(ord('1'), ord('9'))]

    ui_sim = wx.UIActionSimulator()

    for _ in range(1000):
        key_code = random.choice(key_codes)
        ui_sim.KeyDown(key_code)
        ui_sim.KeyUp(key_code)
    try:
        main_window.save_data_to_file('test.json')
    except asn1tools.ConstraintsError:
        pass

    main_window.Close(True)
    wx.GetApp().ExitMainLoop()


class MonkeyTest(TestCase):
    @staticmethod
    def test_monkey():
        if os.getenv('TRAVIS') is not None or os.getenv('GITHUB_ACTIONS') is not None:
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

