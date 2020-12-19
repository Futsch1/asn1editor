import wx


def get_wx_app() -> wx.App:
    app = wx.GetApp()
    if app is None:
        app = wx.App()
    return app
