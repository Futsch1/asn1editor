import typing

import wx


class ImageList:
    def __init__(self):
        self.__image_list = wx.ImageList(16, 16, False, 8)
        self.__index = {}

    def add_bitmap(self, bitmap: wx.Bitmap, name: str):
        self.__index[name] = self.__image_list.Add(bitmap)

    def get_bitmap(self, name: str) -> typing.Optional[wx.Bitmap]:
        if name in self.__index:
            return self.__image_list.GetBitmap(self.__index[name])

    def get_index(self, name: str) -> int:
        return self.__index[name]

    def get_image_list(self) -> wx.ImageList:
        return self.__image_list
