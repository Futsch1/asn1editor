import typing

import asn1tools
import wx
import wx.svg

import asn1editor
from asn1editor.ASN1SpecHandler import ASN1SpecHandler
from asn1editor.Plugin import Plugin
from asn1editor.wxPython.FilePickerHandler import FilePickerHandler
from asn1editor.wxPython.Resources import resource_path
from asn1editor.wxPython.ViewSelect import ViewSelect


class MenuHandler:
    def __init__(self, frame: wx.Frame, plugins: typing.Optional[typing.List[Plugin]]):
        self.__frame = frame
        self.__plugins = plugins
        self.__load_data_item = None
        self.__save_data_item = None
        self.view_select: typing.Optional[ViewSelect] = None

    def build(self, load_spec: typing.Callable, load_data_from_file: typing.Callable, save_data_to_file: typing.Callable, view_changed: typing.Callable):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        load_spec_item: wx.MenuItem = file_menu.Append(wx.ID_ANY, 'Open ASN.1 specification')
        # noinspection PyArgumentList
        image: wx.svg.SVGimage = wx.svg.SVGimage.CreateFromFile(resource_path('icons/open.svg'))
        load_spec_item.SetBitmap(image.ConvertToBitmap(width=16, height=16))
        file_menu.AppendSeparator()
        self.__load_data_item: wx.MenuItem = file_menu.Append(wx.ID_OPEN, 'Load encoded data')
        # noinspection PyArgumentList
        image: wx.svg.SVGimage = wx.svg.SVGimage.CreateFromFile(resource_path('icons/load_encoded.svg'))
        self.__load_data_item.SetBitmap(image.ConvertToBitmap(width=16, height=16))
        self.__load_data_item.Enable(False)
        self.__save_data_item: wx.MenuItem = file_menu.Append(wx.ID_SAVE, 'Save encoded data')
        # noinspection PyArgumentList
        image: wx.svg.SVGimage = wx.svg.SVGimage.CreateFromFile(resource_path('icons/save_encoded.svg'))
        self.__save_data_item.SetBitmap(image.ConvertToBitmap(width=16, height=16))
        self.__save_data_item.Enable(False)
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, 'Exit', 'Exit application')
        # noinspection PyArgumentList
        image: wx.svg.SVGimage = wx.svg.SVGimage.CreateFromFile(resource_path('icons/exit.svg'))
        exit_item.SetBitmap(image.ConvertToBitmap(width=16, height=16))
        menu_bar.Append(file_menu, '&File')

        view_menu = wx.Menu()
        auto_view: wx.MenuItem = view_menu.Append(ViewSelect.AUTO, 'Automatic', kind=wx.ITEM_CHECK)
        auto_view.Check(True)
        groups_view: wx.MenuItem = view_menu.Append(ViewSelect.GROUPS, 'Groups', kind=wx.ITEM_CHECK)
        tree_view: wx.MenuItem = view_menu.Append(ViewSelect.TREE, 'Tree', kind=wx.ITEM_CHECK)
        menu_bar.Append(view_menu, '&View')

        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, 'About')
        self.__frame.Bind(wx.EVT_MENU, self.__about_item_event, about_item)
        menu_bar.Append(help_menu, '&Help')

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
                        toolbar.Bind(wx.EVT_TOOL, self.__tb_menu_event)
                    else:
                        toolbar.AddSeparator()

                    for i, tool in enumerate(tools):
                        if not len(tool[0]):
                            toolbar.AddSeparator()
                        else:
                            bitmap = wx.Bitmap(tool[2])
                            toolbar.AddTool(toolId=plugin_index * 1000 + i, label=tool[0], bitmap=bitmap, shortHelp=tool[1])

        if toolbar is not None:
            toolbar.Realize()

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

        picker = FilePickerHandler(schema_dialog_constructor, load_spec)
        self.__frame.Bind(wx.EVT_MENU, picker.on_menu_click, load_spec_item)

        picker = FilePickerHandler(data_load_dialog_constructor, load_data_from_file)
        self.__frame.Bind(wx.EVT_MENU, picker.on_menu_click, self.__load_data_item)

        picker = FilePickerHandler(data_save_dialog_constructor, save_data_to_file, True)
        self.__frame.Bind(wx.EVT_MENU, picker.on_menu_click, self.__save_data_item)

        self.view_select = ViewSelect(self.__frame, auto_view, groups_view, tree_view, view_changed)

    def enable(self):
        self.__load_data_item.Enable(True)
        self.__save_data_item.Enable(True)

    # noinspection PyUnusedLocal
    def __about_item_event(self, e: wx.Event):
        del e
        dialog = wx.MessageDialog(self, f'''asn1editor {asn1editor.__version__}

Published under MIT License

Copyright (c) 2020 Florian Fetz
https://github.com/Futsch1/asn1editor

Based on eerimoq's asn1tools, used in {asn1tools.version.__version__}
https://github.com/eerimoq/asn1tools
''', style=wx.ICON_INFORMATION | wx.OK, caption='About')
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
