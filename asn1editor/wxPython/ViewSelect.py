import typing
from enum import Enum

import wx


class ViewType(Enum):
    GROUPS = 2
    TREE = 3


class TagInfo(Enum):
    TOOLTIPS = 0
    LABELS = 1


class RadioHandler:
    def __init__(self, names_and_values: typing.List[typing.Tuple[str, int]]):
        self.__names_and_values = names_and_values
        self.__menu_items: typing.Dict[int, wx.MenuItem] = {}

    def append_menu_items(self, menu: wx.Menu, default: Enum):
        for name, value in self.__names_and_values:
            self.__menu_items[value] = menu.Append(wx.ID_ANY, name, kind=wx.ITEM_RADIO)
            if value == default:
                self.__menu_items[value].Check(True)

    def bind(self, frame: wx.Frame, callback: typing.Callable):
        for menu_item in self.__menu_items.values():
            frame.Bind(wx.EVT_MENU, lambda _: callback(), menu_item)

    @property
    def value(self) -> int:
        for enum, menu_item in self.__menu_items.items():
            if menu_item.IsChecked():
                return enum

    @value.setter
    def value(self, val: int):
        self.__menu_items[val].Check(True)


class ViewSelect:
    def __init__(self, frame: wx.Frame, change_callback: typing.Callable):
        self.__view_select_radio = RadioHandler([('Groups', ViewType.GROUPS.value), ('Tree', ViewType.TREE.value)])
        self.__tag_info_radio = RadioHandler([('Tooltips', TagInfo.TOOLTIPS.value), ('Labels', TagInfo.LABELS.value)])

        self.__view_menu = wx.Menu()
        self.__view_select_radio.append_menu_items(self.__view_menu, ViewType.TREE)
        self.__view_menu.AppendSeparator()
        self.__dark_mode: wx.MenuItem = self.__view_menu.Append(wx.ID_ANY, 'Dark mode', kind=wx.ITEM_CHECK)
        self.__view_menu.AppendSeparator()
        tag_info_sub = wx.Menu()
        self.__tag_info_radio.append_menu_items(tag_info_sub, TagInfo.TOOLTIPS)
        self.__view_menu.AppendSubMenu(tag_info_sub, 'Tag information')

        self.__change_callback = change_callback
        frame.Bind(wx.EVT_MENU, self.event_dark_mode, self.__dark_mode)

        self.__view_select_radio.bind(frame, change_callback)
        self.__tag_info_radio.bind(frame, lambda: change_callback(True))

    def get_menu(self) -> wx.Menu:
        return self.__view_menu

    def event_dark_mode(self, _):
        self.__change_callback()

    @property
    def view_type(self) -> ViewType:
        return ViewType(self.__view_select_radio.value)

    @view_type.setter
    def view_type(self, selected: ViewType):
        self.__view_select_radio.value = selected.value

    @property
    def dark_mode(self) -> bool:
        return self.__dark_mode.IsChecked()

    @dark_mode.setter
    def dark_mode(self, dark_mode: bool):
        self.__dark_mode.Check(dark_mode)

    @property
    def tag_info(self) -> TagInfo:
        return TagInfo(self.__tag_info_radio.value)

    @tag_info.setter
    def tag_info(self, tag_info: TagInfo):
        self.__tag_info_radio.value = tag_info.value
