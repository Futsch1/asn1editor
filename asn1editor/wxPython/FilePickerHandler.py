from typing import Callable, Optional

import wx


class FilePickerHandler:
    def __init__(self, file_dialog_factory: Callable, propagator: Optional[Callable]):
        self.__file_dialog_factory = file_dialog_factory
        self.__propagator = propagator
        self.filename = None

    # noinspection PyUnusedLocal
    def on_menu_click(self, e: wx.Event):
        del e
        with self.__file_dialog_factory() as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            filename = file_dialog.GetPath()
            self.file_selected(filename)

    def file_selected(self, filename: Optional[str]):
        self.filename = filename
        if filename is not None and self.__propagator is not None:
            self.__propagator(filename)
