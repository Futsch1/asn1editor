import os
import typing

import wx

from asn1editor.ASN1SpecHandler import ASN1SpecHandler
from asn1editor.Plugin import Plugin
from asn1editor.wxPython import Resources
from asn1editor.wxPython.FilePickerHandler import FilePickerHandler
from asn1editor.wxPython.Resources import plugin_resource_path
from asn1editor.wxPython.ViewSelect import ViewSelect


class MenuHandler:
    def __init__(self, frame: wx.Frame, plugins: typing.Optional[typing.List[Plugin]], about_box_content: str):
        self.__frame = frame
        self.__plugins = plugins
        self.__load_data_item = None
        self.__save_data_item = None
        self.__load_spec = None
        self.__load_last_spec = None
        self.__close_spec_item = None
        self.__recent: typing.Optional[typing.List[typing.List[str]]] = None
        self.__recent_menu: typing.Optional[wx.Menu] = None
        self.__about_box_content = about_box_content
        self.view_select: typing.Optional[ViewSelect] = None

    def build(self, load_spec: typing.Callable, load_data_from_file: typing.Callable, save_data_to_file: typing.Callable, view_changed: typing.Callable):
        self.__load_spec = load_spec
        self.view_select = ViewSelect(self.__frame, view_changed)

        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        load_spec_item: wx.MenuItem = file_menu.Append(wx.ID_ANY, 'Open ASN.1 specification')
        load_spec_item.SetBitmap(Resources.get_bitmap_from_svg('open'))
        self.__close_spec_item = file_menu.Append(wx.ID_ANY, 'Close ASN.1 specification')
        self.__close_spec_item.Enable(False)
        self.__recent_menu = wx.Menu()
        self.__recent_menu.AppendSeparator()
        self.__frame.Bind(wx.EVT_MENU, self.__clear_recent, self.__recent_menu.Append(wx.ID_ANY, 'Clear recent list'))
        recent_submenu: wx.MenuItem = file_menu.AppendSubMenu(self.__recent_menu, 'Open recent')
        recent_submenu.SetBitmap(Resources.get_bitmap_from_svg('recent'))
        self.__load_last_spec: wx.MenuItem = file_menu.Append(wx.ID_ANY, 'Open last specification on startup', kind=wx.ITEM_CHECK)
        file_menu.AppendSeparator()
        self.__load_data_item: wx.MenuItem = file_menu.Append(wx.ID_OPEN, 'Load encoded data')
        self.__load_data_item.SetBitmap(Resources.get_bitmap_from_svg('load_encoded'))
        self.__load_data_item.Enable(False)
        self.__save_data_item: wx.MenuItem = file_menu.Append(wx.ID_SAVE, 'Save encoded data')
        self.__save_data_item.SetBitmap(Resources.get_bitmap_from_svg('save_encoded'))
        self.__save_data_item.Enable(False)
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, 'Exit', 'Exit application')
        exit_item.SetBitmap(Resources.get_bitmap_from_svg('exit'))
        menu_bar.Append(file_menu, '&File')

        menu_bar.Append(self.view_select.get_menu(), '&View')

        self.__frame.SetMenuBar(menu_bar)

        toolbar: typing.Optional[wx.ToolBar] = None

        if self.__plugins is not None:
            for plugin_index, plugin in enumerate(self.__plugins):
                plugin_menu = wx.Menu()
                menus = plugin.get_menus()
                for i, menu in enumerate(menus):
                    if not len(menu[0]):
                        plugin_menu.AppendSeparator()
                    else:
                        menu_item: wx.MenuItem = plugin_menu.Append(plugin_index * 1000 + i, menu[0])
                        if menu[1] is not None:
                            self.__frame.Bind(wx.EVT_MENU, self.__plugin_menu_event, menu_item)
                        else:
                            menu_item.Enable(False)

                menu_bar.Append(plugin_menu, plugin.get_name())

                tools = plugin.get_tools()
                if len(tools):
                    if toolbar is None:
                        toolbar = self.__frame.CreateToolBar()
                        toolbar.SetToolSeparation(8)
                        toolbar.Bind(wx.EVT_TOOL, self.__tb_menu_event)
                    else:
                        toolbar.AddSeparator()

                    labels = False

                    for i, tool in enumerate(tools):
                        if not len(tool):
                            toolbar.AddSeparator()
                        else:
                            bitmap = wx.Bitmap(plugin_resource_path(tool[2]))
                            labels |= len(tool[0]) > 0
                            toolbar.AddTool(toolId=plugin_index * 1000 + i, label=tool[0], bitmap=bitmap, shortHelp=tool[1])
                    if labels:
                        toolbar.SetWindowStyle(wx.TB_TEXT | wx.TB_HORIZONTAL)
                        pass

        if toolbar is not None:
            toolbar.Realize()

        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, 'About')
        self.__frame.Bind(wx.EVT_MENU, self.__about_item_event, about_item)
        menu_bar.Append(help_menu, '&Help')

        # Event binding
        def schema_dialog_constructor() -> wx.FileDialog:
            return wx.FileDialog(self.__frame, "ASN.1 schema", wildcard="ASN.1 files (*.asn)|*.asn",
                                 style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)

        def data_load_dialog_constructor() -> wx.FileDialog:
            extensions = ';'.join(ASN1SpecHandler.get_extensions())
            return wx.FileDialog(self.__frame, "ASN.1 encoded file", wildcard=f"ASN.1 encoded ({extensions})|{extensions}",
                                 style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        def data_save_dialog_constructor() -> wx.FileDialog:
            extensions = ';'.join(ASN1SpecHandler.get_extensions())
            return wx.FileDialog(self.__frame, "ASN.1 encoded file", wildcard=f"ASN.1 encoded ({extensions})|{extensions}", style=wx.FD_SAVE)

        self.__frame.Bind(wx.EVT_MENU, self.__exit, exit_item)

        self.__frame.Bind(wx.EVT_MENU, self.__close_spec, self.__close_spec_item)

        picker = FilePickerHandler(schema_dialog_constructor, load_spec)
        self.__frame.Bind(wx.EVT_MENU, picker.on_menu_click, load_spec_item)

        picker = FilePickerHandler(data_load_dialog_constructor, load_data_from_file)
        self.__frame.Bind(wx.EVT_MENU, picker.on_menu_click, self.__load_data_item)

        picker = FilePickerHandler(data_save_dialog_constructor, save_data_to_file, True)
        self.__frame.Bind(wx.EVT_MENU, picker.on_menu_click, self.__save_data_item)

    def enable(self, enable: bool = True):
        self.__load_data_item.Enable(enable)
        self.__save_data_item.Enable(enable)
        self.__close_spec_item.Enable(enable)

    @property
    def recent(self) -> typing.List[typing.List[str]]:
        return self.__recent

    @recent.setter
    def recent(self, recent_list: typing.List[typing.List[str]]):
        self.__recent = recent_list

        for recent_list in reversed(self.__recent):
            self.__prepend_recent_to_menu(recent_list)

    def add_recent(self, filename: str, typename: str):
        recent = [filename, typename]
        if recent in self.__recent:
            # If item is already in recent list, move it to the front
            recent_string = self.__get_recent_string(recent)
            menu_item = self.__recent_menu.FindItem(recent_string)
            self.__recent_menu.Remove(menu_item)
            self.__recent.remove(recent)

        self.__recent.insert(0, recent)
        self.__prepend_recent_to_menu(recent)

    @staticmethod
    def __get_recent_string(recent: typing.List[str]):
        return f'{os.path.basename(recent[0])} {recent[1]} ({recent[0]})'

    def __prepend_recent_to_menu(self, recent: typing.List[str]):
        recent_item = self.__recent_menu.Prepend(wx.ID_ANY, self.__get_recent_string(recent))
        self.__frame.Bind(wx.EVT_MENU, lambda _: self.__load_spec(recent[0], recent[1]), recent_item)

    def __clear_recent(self, _: wx.Event):
        menu_items = self.__recent_menu.GetMenuItems()
        for menu_item in menu_items:
            if menu_item.GetKind() == wx.ITEM_SEPARATOR:
                break
            self.__recent_menu.Remove(menu_item)

        self.__recent = []

    @property
    def load_last(self) -> bool:
        return self.__load_last_spec.IsChecked()

    @load_last.setter
    def load_last(self, load_last: bool):
        self.__load_last_spec.Check(load_last)

    # noinspection PyUnusedLocal
    def __about_item_event(self, e: wx.Event):
        del e
        dialog = wx.MessageDialog(self.__frame, self.__about_box_content, style=wx.ICON_INFORMATION | wx.OK, caption='About')
        dialog.ShowModal()

    def __tb_menu_event(self, e):
        menu_id = e.GetId()
        plugin_index = menu_id // 1000
        self.__plugins[plugin_index].get_tools()[menu_id % 1000][3]()

    def __plugin_menu_event(self, e):
        menu_id = e.GetId()
        plugin_index = menu_id // 1000
        self.__plugins[plugin_index].get_menus()[menu_id % 1000][1]()

    # noinspection PyUnusedLocal
    def __exit(self, e: wx.Event):
        del e
        self.__frame.Close()

    def __close_spec(self, _):
        self.enable(False)
        self.__load_spec(None)
