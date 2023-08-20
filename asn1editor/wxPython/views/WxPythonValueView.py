import typing

import wx

from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractViewFactory import TypeInfo, Styles
from asn1editor.wxPython.views.WxPythonView import WxPythonView, ControlList


class WxPythonValueView(WxPythonView, ValueInterface):
    def __init__(self, type_info: TypeInfo, controls: ControlList):
        super(WxPythonValueView, self).__init__(type_info, controls)

    def get_sizers(self, recursive: bool) -> typing.Tuple[wx.Sizer, typing.Optional[wx.Sizer]]:
        sizer = self._create_sizer()
        value_sizer = wx.BoxSizer()
        value_sizer.Add(self._controls['value'], proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        if self._controls.get('style') & Styles.HIDDEN:
            sizer.ShowItems(False)
            value_sizer.ShowItems(False)

        return sizer, value_sizer

    def register_change_event(self, callback: typing.Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            self.__update_tooltip()
            callback()

        self._controls['value'].Bind(wx.EVT_TEXT, event_closure)

    def get_value(self) -> str:
        return self._controls['value'].GetValue()

    def set_value(self, val: str):
        self._controls['value'].SetValue(val)
        self.__update_tooltip()

    def enable(self, enabled: bool):
        self._controls['value'].Enable(enabled)

    def __update_tooltip(self):
        if isinstance(self.get_value(), str) and len(self.get_value()) > 10:
            tool_tip = self._controls['value'].GetToolTip()
            if tool_tip is not None:
                previous_tooltip = self._controls['value'].GetToolTip().GetTip().split('\n')
                previous_tooltip = previous_tooltip[-1]
            else:
                previous_tooltip = ''
            self._controls['value'].SetToolTip('\n'.join([self.get_value(), previous_tooltip]))


class WxPythonValueSelectionView(WxPythonValueView):
    def __init__(self, type_info: TypeInfo, controls: ControlList):
        super(WxPythonValueSelectionView, self).__init__(type_info, controls)

    def get_value(self) -> str:
        return self._controls['value'].GetStringSelection()

    def set_value(self, val: str):
        self._controls['value'].SetStringSelection(val)
