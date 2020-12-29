import typing

import wx


class SingleFileDropTarget(wx.FileDropTarget):

    def __init__(self, callback: typing.Callable):
        wx.FileDropTarget.__init__(self)
        self.__callback = callback

    def OnDropFiles(self, _, __, filenames):
        if len(filenames) == 1:
            wx.CallAfter(self.__callback, filenames[0])
            return True
        return False
