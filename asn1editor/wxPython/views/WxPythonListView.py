import typing
from typing import Callable

import wx

from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import ListView
from asn1editor.view.AbstractViewFactory import TypeInfo
from asn1editor.wxPython.views.WxPythonContainerView import WxPythonContainerView
from asn1editor.wxPython.views.WxPythonView import WxPythonView, ControlList


class WxPythonListView(WxPythonContainerView, ListView, ValueInterface):
    icon = 'sequence_of'

    def __init__(self, type_info: TypeInfo, controls: ControlList, parent: wx.Window):
        super(WxPythonListView, self).__init__(type_info, controls, parent)

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            self._controls['value'].GetTopLevelParent().Freeze()
            callback()
            self._controls['value'].GetTopLevelParent().Thaw()

        self._controls['value'].Bind(wx.EVT_SPINCTRL, event_closure)

    def get_value(self) -> str:
        return self._controls['value'].GetValue()

    def set_value(self, val: str):
        self._controls['value'].SetValue(val)

    def enable(self, enabled: bool):
        self._controls['value'].Enable(enabled)
        super(WxPythonListView, self).enable(enabled)

    def add(self, view: WxPythonView):
        self._children.append(view)
        view.set_visible(self.get_has_value(), recursive=True)
        self.structure_changed()

    def remove(self, view: WxPythonView):
        self._children.remove(view)
        view.destroy()
        self.structure_changed()

    def get_sizers(self, recursive: bool) -> typing.Tuple[wx.Sizer, typing.Optional[wx.Sizer]]:
        sizer = self._create_sizer(wx.VERTICAL)
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sub_sizer.Add(self._controls['num_elements'], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        sub_sizer.Add(self._controls['value'], border=5, flag=wx.ALL)
        sizer.Add(sub_sizer)

        sizer.Add(self._get_container_sizer(recursive, self._children))

        return sizer, None
