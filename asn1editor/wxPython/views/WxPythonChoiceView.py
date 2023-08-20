import typing
from typing import Optional, Callable

import wx

from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import ChoiceView
from asn1editor.view.AbstractViewFactory import TypeInfo
from asn1editor.wxPython.views.WxPythonView import WxPythonView, ControlList


class WxPythonChoiceView(WxPythonView, ChoiceView, ValueInterface):
    icon = 'choice'

    def __init__(self, type_info: TypeInfo, controls: ControlList):
        super(WxPythonChoiceView, self).__init__(type_info, controls, True)
        self._view: Optional[WxPythonView] = None

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            self._controls['value'].GetTopLevelParent().Freeze()
            callback()
            self._controls['value'].GetTopLevelParent().Thaw()

        self._controls['value'].Bind(wx.EVT_COMBOBOX, event_closure)

    def get_value(self) -> str:
        return self._controls['value'].GetStringSelection()

    def set_value(self, val: str):
        self._controls['value'].SetStringSelection(val)

    def enable(self, enabled: bool):
        self._controls['value'].Enable(enabled)
        if self._view is not None:
            self._view.set_visible(enabled)
            self.structure_changed()

    def set_view(self, view: WxPythonView):
        if self._view is not None:
            self._view.destroy()

        self._view = view

        self._view.set_visible(self.get_has_value())

        self.structure_changed()

    def get_view(self) -> WxPythonView:
        return self._view

    def get_sizers(self, recursive: bool) -> typing.Tuple[wx.Sizer, typing.Optional[wx.Sizer]]:
        sizer = self._create_sizer(wx.VERTICAL)
        sizer.Add(self._controls['value'], border=5)

        if recursive or not self._view.container:
            content_sizer = wx.BoxSizer(wx.VERTICAL)
            left_sizer, right_sizer = self._view.get_sizers(recursive)
            content_sizer.Add(left_sizer, border=5, flag=wx.EXPAND)
            if right_sizer is not None:
                content_sizer.Add(right_sizer, border=5, flag=wx.EXPAND)

            if not self.get_has_value():
                content_sizer.Hide(left_sizer)
                if right_sizer is not None:
                    content_sizer.Hide(right_sizer)

            sizer.Add(content_sizer)

        return sizer, None

    def destroy(self):
        super(WxPythonChoiceView, self).destroy()
        if self._view is not None:
            self._view.destroy()

    def set_visible(self, visible, recursive=True):
        super(WxPythonChoiceView, self).set_visible(visible, recursive)
        if recursive or not self._view.container:
            self._view.set_visible(visible and self.get_has_value(), recursive)
