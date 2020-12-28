import time

import wx


def get_wx_app() -> wx.App:
    app = wx.GetApp()
    if app is not None:
        app.Destroy()
        time.sleep(1)

    app = wx.App()
    return app
