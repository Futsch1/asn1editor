import os
import sys
import typing

import wx
import wx.svg

import asn1editor
from asn1editor.ASN1SpecHandler import ASN1SpecHandler
from asn1editor.Plugin import Plugin
from asn1editor.PluginInterface import PluginInterface
from asn1editor.wxPython import Environment, Resources
from asn1editor.wxPython import WxPythonViewFactory
from asn1editor.wxPython.FilePickerHandler import FilePickerHandler
from asn1editor.wxPython.ImageList import ImageList
from asn1editor.wxPython.MenuHandler import MenuHandler
from asn1editor.wxPython.SingleFileDropTarget import SingleFileDropTarget
from asn1editor.wxPython.Styler import Styler
from asn1editor.wxPython.TreeView import TreeView
from asn1editor.wxPython.WxPythonViews import WxPythonView


class MainWindow(wx.Frame, PluginInterface):
    def __init__(self, plugins: typing.Optional[typing.List[Plugin]] = None, title=f'ASN.1 editor {asn1editor.__version__}', enable_load_last=True):
        super(MainWindow, self).__init__(None, title=title)

        Environment.load()
        Resources.image_list = ImageList()

        if plugins is not None:
            for plugin in plugins:
                plugin.connect(self)

        self._status_bar = self.CreateStatusBar()

        self._menu_handler = MenuHandler(self, plugins)

        self._menu_handler.build(self.load_spec, self.load_data_from_file, self.save_data_to_file, self._structure_changed)
        self.Bind(wx.EVT_CLOSE, self.close)

        self.SetSize(wx.Size(Environment.settings.get('size', (500, 800))))
        self.Maximize(Environment.settings.get('maximized', True))
        self.SetPosition(wx.Point(Environment.settings.get('position', (0, 0))))
        screen_rect: wx.Rect = self.GetScreenRect()
        center = screen_rect.GetTopLeft() + (screen_rect.GetWidth() // 2, screen_rect.GetHeight() // 2)
        if wx.Display.GetFromPoint(center) == wx.NOT_FOUND:
            self.SetPosition(wx.Point(0, 0))
        self._menu_handler.view_select.selected = Environment.settings.get('view', 1)
        self._menu_handler.recent = Environment.settings.get('recent', [])
        self._menu_handler.load_last = Environment.settings.get('load_last', True)

        self.__asn1_handler = None

        self.__model = None
        self.__view = None
        self.__controller = None
        self.__type_name = None
        self.__file_name = None
        self.__tree_view: typing.Optional[TreeView] = None
        self.__content_panel: typing.Optional[wx.ScrolledWindow] = None

        self.__progress_window: typing.Optional[wx.ProgressDialog] = None

        self.SetDropTarget(SingleFileDropTarget(self.__file_dropped))
        self.SetAutoLayout(True)
        self.SetSizer(wx.BoxSizer(wx.HORIZONTAL))

        # noinspection SpellCheckingInspection
        sys.excepthook = self.__exception_handler

        WxPythonView.structure_changed = None

        if self._menu_handler.load_last and enable_load_last:
            # noinspection PyBroadException
            try:
                self._menu_handler.load_most_recent()
            except Exception:
                pass

    def __file_dropped(self, file_name: str):
        if self.__asn1_handler is not None:
            self.load_data_from_file(file_name)
        else:
            self.load_spec(file_name)

    def load_spec(self, file_name: str, type_name: typing.Optional[str] = None):
        wx.App.Get().ProcessPendingEvents()
        # Spec file loaded, compile it to show a selection of type names
        if not self.__asn1_handler or file_name not in self.__asn1_handler.get_filename():
            try:
                self.__asn1_handler = ASN1SpecHandler(file_name)
            except FileNotFoundError:
                self.show_message(f'File {file_name} not found', 'Error', PluginInterface.MessageType.ERROR)
                return

        if type_name is None:
            types = self.__asn1_handler.get_types()
            dialog = wx.SingleChoiceDialog(self, 'Select type from ASN.1 file', 'Select type', types)
            try:
                if dialog.ShowModal() == wx.ID_OK:
                    self.__type_name = dialog.GetStringSelection()
            finally:
                dialog.Destroy()
        else:
            self.__type_name = type_name

        if self.__type_name is not None:
            self._menu_handler.add_recent(os.path.abspath(file_name), self.__type_name)

            self._status_bar.SetStatusText(f'Loaded {file_name}')
            self.__file_name = file_name

            if self.__view is not None:
                self.__view.realize().destroy()
                self.__content_panel.Destroy()
            if self.__tree_view is not None:
                self.__tree_view.destroy()

            styler = Styler(os.path.splitext(file_name)[0] + '.style')

            WxPythonView.structure_changed = lambda x: None

            self.__content_panel = wx.ScrolledWindow(self, style=wx.HSCROLL | wx.VSCROLL)
            self.__content_panel.SetScrollbars(15, 15, 50, 50)
            self.__content_panel.SetAutoLayout(True)
            self.__content_panel.SetSizer(wx.BoxSizer(wx.VERTICAL))

            view_factory = WxPythonViewFactory.WxPythonViewFactory(self.__content_panel, styler)

            self.Freeze()

            self.__view, self.__controller = self.__asn1_handler.create_mvc_for_type(self.__type_name, view_factory)
            self.__tree_view = TreeView(self, self.__content_panel, self.__type_name)

            self.Thaw()

            WxPythonView.structure_changed = self._structure_changed
            self._structure_changed()

            self._menu_handler.enable()

    def _structure_changed(self):
        if self.__type_name is None:
            return

        self.Freeze()

        sizer = self.GetSizer()
        sizer.Clear()
        content_panel_sizer: wx.Sizer = self.__content_panel.GetSizer()
        content_panel_sizer.Clear()

        if self._menu_handler.view_select.selected == self._menu_handler.view_select.TREE:

            tree_ctrl = self.__tree_view.get_ctrl(self.__view.realize())

            sizer.Add(tree_ctrl, proportion=1, flag=wx.ALL | wx.EXPAND)
            sizer.Add(self.__content_panel, proportion=2, flag=wx.ALL | wx.EXPAND)
        else:
            self.__tree_view.hide()

            self.__view.realize().set_visible(True, recursive=True)
            content_sizer = self.__view.realize().get_sizer(recursive=True)
            content_panel_sizer.Add(content_sizer, flag=wx.ALL | wx.EXPAND, border=5)

            self.__content_panel.SetSizerAndFit(content_panel_sizer)

            sizer.Add(self.__content_panel, flag=wx.ALL | wx.EXPAND)

        self.SetSizer(sizer)

        self.Refresh()
        self.PostSizeEvent()

        self.Thaw()

    def load_data_from_file(self, file_name: str):
        self.__controller.model_to_view(self.__asn1_handler.load_data_file(file_name))
        self._status_bar.SetStatusText(f'Loaded {file_name} for {self.__type_name}')

    def save_data_to_file(self, file_name: str):
        self.__asn1_handler.save_data_file(file_name, self.__controller.view_to_model())

    def show_data(self, data: bytes, codec: str):
        self.__controller.model_to_view(self.__asn1_handler.get_model_from_data(data, codec))
        self._status_bar.SetStatusText(f'Loaded data for {self.__type_name}')

    def file_picker(self, message: str, wildcard: str, open_: bool) -> typing.Optional[str]:
        def dialog_constructor() -> wx.FileDialog:
            return wx.FileDialog(self, message, wildcard=wildcard,
                                 style=(wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) if open_ else wx.FD_SAVE)

        picker = FilePickerHandler(dialog_constructor, None, not open_)
        picker.on_menu_click(wx.EVT_MENU)
        return picker.filename

    def dir_picker(self, message: str) -> typing.Optional[str]:
        def dialog_constructor() -> wx.DirDialog:
            return wx.DirDialog(self, message,
                                style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        picker = FilePickerHandler(dialog_constructor, None)
        picker.on_menu_click(wx.EVT_MENU)
        return picker.filename

    def encode_data(self, codec: str) -> bytes:
        return self.__asn1_handler.get_data_from_model(self.__controller.view_to_model(), codec)

    def get_spec_filename(self) -> str:
        return self.__file_name

    def get_typename(self) -> str:
        return self.__type_name

    def get_spec(self, codec: str):
        return self.__asn1_handler.get_compiled(codec)

    def text_entry(self, message: str, default: typing.Optional[str] = None) -> typing.Optional[str]:
        with wx.TextEntryDialog(self, message) as text_dialog:
            if default is not None:
                text_dialog.SetValue(default)
            if text_dialog.ShowModal() == wx.ID_CANCEL:
                return
            return text_dialog.GetValue()

    def choice_entry(self, message: str, caption: str, choices: typing.List[str], default: typing.Optional[str] = None) -> typing.Optional[str]:
        with wx.SingleChoiceDialog(self, message, caption, choices=choices) as choice_dialog:
            if default is not None:
                try:
                    choice_dialog.SetSelection(choices.index(default))
                except ValueError:
                    pass
            if choice_dialog.ShowModal() == wx.ID_CANCEL:
                return
            return choice_dialog.GetStringSelection()

    def show_status(self, message: str):
        self._status_bar.SetStatusText(message)

    def show_message(self, message: str, caption: str, message_type: PluginInterface.MessageType) -> bool:
        style = wx.CENTER | {PluginInterface.MessageType.WARNING: wx.OK | wx.ICON_WARNING,
                             PluginInterface.MessageType.INFO: wx.OK | wx.ICON_INFORMATION,
                             PluginInterface.MessageType.ERROR: wx.OK | wx.ICON_ERROR,
                             PluginInterface.MessageType.QUESTION: wx.YES_NO | wx.ICON_QUESTION}[message_type]
        ret = wx.MessageBox(message, caption, style=style)
        return True if message_type != PluginInterface.MessageType.QUESTION else wx.YES == ret

    def show_progress(self, message: str, caption: str, max_progress: typing.Optional[int] = None):
        self.__progress_window = wx.ProgressDialog(caption, message, maximum=max_progress if max_progress else 100, style=wx.PD_APP_MODAL | wx.PD_CAN_ABORT)

    def update_progress(self, message: typing.Optional[str] = None, close: bool = False, progress: typing.Optional[int] = None) -> bool:
        running = False
        if self.__progress_window:
            if progress is not None:
                running = self.__progress_window.Update(progress, newmsg=message)[0]
            else:
                running = self.__progress_window.Pulse()[0]
        if close:
            self.__progress_window.Close()
            self.__progress_window = None

        return running

    def get_settings(self) -> dict:
        return Environment.settings.setdefault('Plugin', {})

    def __exception_handler(self, exc_type, value, trace):
        import traceback
        trace = ''.join(traceback.format_exception(exc_type, value, trace))
        print(trace)

        message = f'{value}\n\n{str(exc_type)}'
        exception_str = f'{message}\n\n{trace}'
        wx.MessageBox(message, 'Error', wx.OK | wx.ICON_ERROR, parent=self)
        self._status_bar.SetStatusText(f'Error: {value}')
        Environment.log_error(exception_str)

    # noinspection PyUnusedLocal
    def close(self, e: wx.Event):
        Environment.settings['size'] = (self.GetSize().Get())
        Environment.settings['maximized'] = self.IsMaximized()
        Environment.settings['position'] = self.GetPosition().Get()
        Environment.settings['view'] = self._menu_handler.view_select.selected
        Environment.settings['recent'] = self._menu_handler.recent
        Environment.settings['load_last'] = self._menu_handler.load_last

        Environment.save()

        self.Destroy()
