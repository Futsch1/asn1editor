import typing

import wx


class ViewSelect:
    AUTO = 1
    GROUPS = 2
    TREE = 3

    def __init__(self, frame: wx.Frame, auto_item: wx.MenuItem, groups_item: wx.MenuItem, tree_item: wx.MenuItem, change_callback: typing.Callable):
        self.__auto_item = auto_item
        self.__auto_item.Enable(False)
        self.__groups_item = groups_item
        self.__tree_item = tree_item
        self.__change_callback = change_callback
        frame.Bind(wx.EVT_MENU, self.event, auto_item)
        frame.Bind(wx.EVT_MENU, self.event, groups_item)
        frame.Bind(wx.EVT_MENU, self.event, tree_item)

        self.__auto_item.Check(False)
        self.__groups_item.Check(False)
        self.__tree_item.Check(True)

    def event(self, e: wx.Event):
        self.selected = e.GetId()
        self.__change_callback()

    @property
    def selected(self):
        return self.AUTO if self.__auto_item.IsChecked() else self.GROUPS if self.__groups_item.IsChecked() else self.TREE

    @selected.setter
    def selected(self, selected):
        self.__auto_item.Check(selected == self.AUTO)
        self.__groups_item.Check(selected == self.GROUPS)
        self.__tree_item.Check(selected == self.TREE)
