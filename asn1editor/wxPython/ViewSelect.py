import typing
from enum import Enum

import wx


class ViewType(Enum):
    GROUPS = 2
    TREE = 3


class ViewSelect:

    def __init__(self, frame: wx.Frame, groups_item: wx.MenuItem, tree_item: wx.MenuItem, dark_mode: wx.MenuItem,
                 change_callback: typing.Callable):
        self.__groups_item = groups_item
        self.__tree_item = tree_item
        self.__dark_mode = dark_mode
        self.__change_callback = change_callback
        frame.Bind(wx.EVT_MENU, lambda _: self.event(ViewType.GROUPS.value), groups_item)
        frame.Bind(wx.EVT_MENU, lambda _: self.event(ViewType.TREE.value), tree_item)
        frame.Bind(wx.EVT_MENU, self.event_dark_mode, dark_mode)

        self.__groups_item.Check(False)
        self.__tree_item.Check(True)

    def event(self, selected: int):
        self.selected = selected
        self.__change_callback()

    def event_dark_mode(self, _):
        self.__change_callback()

    @property
    def selected(self) -> ViewType:
        return ViewType.GROUPS if self.__groups_item.IsChecked() else ViewType.TREE

    @selected.setter
    def selected(self, selected: int):
        self.__groups_item.Check(selected == ViewType.GROUPS.value)
        self.__tree_item.Check(selected == ViewType.TREE.value)

    @property
    def dark_mode(self) -> bool:
        return self.__dark_mode.IsChecked()

    @dark_mode.setter
    def dark_mode(self, dark_mode: bool):
        self.__dark_mode.Check(dark_mode)
