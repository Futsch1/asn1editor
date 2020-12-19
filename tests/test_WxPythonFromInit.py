import sys
import threading
from time import sleep
from unittest import TestCase

import wx

import asn1editor
from tests import testHelper


def delay(app: wx.App):
    sleep(1)
    while app.GetTopWindow():
        app.GetTopWindow().Close(True)
    app.ExitMainLoop()


class WxPythonFromInit(TestCase):
    @staticmethod
    def test_open():
        app = testHelper.get_wx_app()

        action_thread = threading.Thread(target=delay, args=[app])
        action_thread.start()

        sys.argv = ['asn1editor']
        asn1editor._wx_python_editor()
        action_thread.join()

        app.Destroy()
