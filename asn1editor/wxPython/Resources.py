import os
import sys
import typing

from asn1editor.wxPython.ImageList import ImageList

image_list: typing.Optional[ImageList] = None


def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource required for PyInstaller """
    # noinspection SpellCheckingInspection
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
