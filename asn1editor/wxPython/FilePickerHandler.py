import os
from typing import Callable, Optional, List, Union

import wx

from . import Environment


class FilePickerHandler:
    def __init__(self, file_dialog_factory: Callable, propagator: Optional[Callable], overwrite_question: bool = False):
        self.__file_dialog_factory = file_dialog_factory
        self.__propagator = propagator
        self.__overwrite_question = overwrite_question
        self.filename = None

    # noinspection PyUnusedLocal
    def on_menu_click(self, e: wx.Event):
        del e
        with self.__file_dialog_factory() as file_dialog:
            initial_dir = Environment.settings.get(file_dialog.GetMessage())
            if initial_dir is not None:
                file_dialog.SetPath(initial_dir + '/')
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            if hasattr(file_dialog, 'GetPaths'):
                filenames = file_dialog.GetPaths()
            else:
                filenames = [file_dialog.GetPath()]
            Environment.settings[file_dialog.GetMessage()] = os.path.dirname(filenames[0])
            filenames = filenames if len(filenames) > 1 else filenames[0]
            self.file_selected(filenames, file_dialog.GetParent())

    def file_selected(self, filename: Union[str, List[str]], window: wx.Window):
        use_filename = True
        if self.__overwrite_question and os.path.exists(filename):
            use_filename = False
            with wx.MessageDialog(window, f'File {os.path.basename(filename)} already exists.\n\nDo you want to replace it?',
                                  style=wx.YES | wx.NO | wx.NO_DEFAULT | wx.ICON_WARNING) as question_dialog:
                if question_dialog.ShowModal() == wx.ID_YES:
                    use_filename = True

        if use_filename:
            self.filename = filename
            if self.__propagator is not None:
                self.__propagator(filename)
