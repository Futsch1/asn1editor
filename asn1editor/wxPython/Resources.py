import os
import sys
import typing

import wx
import wx.svg

from asn1editor.wxPython.ImageList import ImageList

image_list: typing.Optional[ImageList] = None


def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource required for PyInstaller """
    # noinspection SpellCheckingInspection
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def plugin_resource_path(relative_path: str) -> str:
    """ Get absolute path to resource required for PyInstaller """
    # noinspection SpellCheckingInspection
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.argv[0])))
    return os.path.join(base_path, relative_path)


def get_bitmap_from_svg(bitmap_name) -> wx.Bitmap:
    # noinspection PyArgumentList
    image: wx.svg.SVGimage = wx.svg.SVGimage.CreateFromFile(resource_path(f'icons/{bitmap_name}.svg'))
    bitmap = image.ConvertToBitmap(width=16, height=16)
    image_list.add_bitmap(bitmap, bitmap_name)
    return bitmap
