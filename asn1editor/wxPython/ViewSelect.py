import typing
from enum import Enum

import wx


class ViewType(Enum):
    AUTO = 1
    GROUPS = 2
    TREE = 3


class ViewSelect:

    def __init__(self, frame: wx.Frame, auto_item: wx.MenuItem, groups_item: wx.MenuItem, tree_item: wx.MenuItem, change_callback: typing.Callable):
        self.__auto_item = auto_item
        self.__auto_item.Enable(False)
        self.__groups_item = groups_item
        self.__tree_item = tree_item
        self.__change_callback = change_callback
        frame.Bind(wx.EVT_MENU, lambda _: self.event(ViewType.AUTO.value), auto_item)
        frame.Bind(wx.EVT_MENU, lambda _: self.event(ViewType.GROUPS.value), groups_item)
        frame.Bind(wx.EVT_MENU, lambda _: self.event(ViewType.TREE.value), tree_item)

        self.__auto_item.Check(False)
        self.__groups_item.Check(False)
        self.__tree_item.Check(True)

    def event(self, selected: int):
        self.selected = selected
        self.__change_callback()

    @property
    def selected(self):
        return ViewType.AUTO if self.__auto_item.IsChecked() else ViewType.GROUPS if self.__groups_item.IsChecked() else ViewType.TREE

    @selected.setter
    def selected(self, selected: int):
        self.__auto_item.Check(selected == ViewType.AUTO.value)
        self.__groups_item.Check(selected == ViewType.GROUPS.value)
        self.__tree_item.Check(selected == ViewType.TREE.value)
