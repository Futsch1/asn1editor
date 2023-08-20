import typing

import wx

from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractViewFactory import TypeInfo
from asn1editor.wxPython.views.WxPythonView import WxPythonView, ControlList


class WxPythonBooleanView(WxPythonView, ValueInterface):
    def __init__(self, type_info: TypeInfo, controls: ControlList):
        super(WxPythonBooleanView, self).__init__(type_info, controls)

    def register_change_event(self, callback: typing.Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        self._controls['value'].Bind(wx.EVT_CHECKBOX, event_closure)

    def get_value(self) -> bool:
        return self._controls['value'].GetValue()

    def set_value(self, val: bool):
        self._controls['value'].SetValue(val)

    def enable(self, enabled: bool):
        self._controls['value'].Enable(enabled)

    def get_sizers(self, recursive: bool) -> typing.Tuple[wx.Sizer, typing.Optional[wx.Sizer]]:
        sizer = self._create_sizer()
        value_sizer = wx.BoxSizer()
        value_sizer.Add(self._controls['value'], proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        return sizer, value_sizer
