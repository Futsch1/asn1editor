import typing
from typing import List

import wx

from asn1editor.view.AbstractView import ContainerView
from asn1editor.view.AbstractViewFactory import TypeInfo
from asn1editor.wxPython.views.WxPythonView import WxPythonView, ControlList


class WxPythonContainerView(WxPythonView, ContainerView):
    icon = 'sequence'

    def __init__(self, type_info: TypeInfo, controls: ControlList, parent: wx.Window):
        super(WxPythonContainerView, self).__init__(type_info, controls, container=True)
        self._children: List[WxPythonView] = []
        self._parent = parent

    def get_sizers(self, recursive: bool) -> typing.Tuple[wx.Sizer, typing.Optional[wx.Sizer]]:
        if recursive and self.get_has_value() and self._controls['name'].IsShown():
            sizer = wx.StaticBoxSizer(wx.VERTICAL, self._parent, self._type_info.name)
        else:
            sizer = wx.BoxSizer(wx.VERTICAL)

        if 'optional' not in self._controls:
            self._controls['icon'].Show(False)
            self._controls['name'].Show(False)
        else:
            name_sizer = wx.BoxSizer(wx.HORIZONTAL)
            name_sizer.Add(self._controls['icon'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=2)
            name_sizer.Add(self._controls['name'], flag=wx.ALL, border=5)
            sizer.Add(name_sizer)

        sizer.Add(self._get_container_sizer(recursive, self._children))

        return sizer, None

    def add_child(self, view: WxPythonView):
        self._children.append(view)
        view.set_visible(self.get_has_value(), recursive=True)

    def enable(self, enabled: bool):
        for child in self._children:
            if child.get_has_value():
                child.enable(enabled)
            child.set_visible(enabled, recursive=True)
        self.structure_changed()

    def get_children(self) -> List[WxPythonView]:
        return self._children

    def destroy(self):
        super(WxPythonContainerView, self).destroy()
        for child in self._children:
            child.destroy()

    def set_visible(self, visible, recursive=True):
        super(WxPythonContainerView, self).set_visible(visible, recursive)
        for child in self._children:
            if recursive or not child.container:
                child.set_visible(visible and self.get_has_value(), recursive)
