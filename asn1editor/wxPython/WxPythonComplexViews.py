from typing import Optional, List, Callable

import wx

from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import ContainerView, ListView, ChoiceView
from asn1editor.wxPython.WxPythonViews import WxPythonView, ControlList


class WxPythonContainerView(WxPythonView, ContainerView):
    def __init__(self, name: str, controls: ControlList, parent: wx.Window):
        super(WxPythonContainerView, self).__init__(name, controls, container=True)
        self._children: List[WxPythonView] = []
        self._parent = parent

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        if recursive:
            sizer = wx.StaticBoxSizer(wx.VERTICAL, self._parent, self._name)
        else:
            sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self._controls['icon'], flag=wx.ALL)
        sizer.Add(self._controls['name'], flag=wx.ALL, border=5)
        if 'optional' not in self._controls:
            sizer.Hide(self._controls['name'])

        if self.get_has_value():
            if recursive:
                container_sizer = wx.FlexGridSizer(cols=2, vgap=8, hgap=8)
                sizer.Add(container_sizer)
            else:
                container_sizer = sizer

            for child in self._children:
                if recursive or not child._container:
                    container_sizer.Add(child.get_sizer(recursive))
        else:
            hide_sizer = wx.BoxSizer(wx.HORIZONTAL)
            for child in self._children:
                child_sizer = child.get_sizer(True)
                hide_sizer.Add(child_sizer)
                hide_sizer.Hide(child_sizer, recursive=True)
            sizer.Add(hide_sizer)

        return sizer

    def add_child(self, view: WxPythonView):
        self._children.append(view)

    def enable(self, enabled: bool):
        pass

    def get_children(self) -> List[WxPythonView]:
        return self._children


class WxPythonListView(WxPythonView, ListView, ValueInterface):
    def __init__(self, name: str, controls: ControlList, parent: wx.Window):
        super(WxPythonListView, self).__init__(name, controls, True)
        self._children: List[WxPythonView] = []
        self._parent = parent

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        self._controls['value'].Bind(wx.EVT_SPINCTRL, event_closure)

    def get_value(self) -> str:
        return self._controls['value'].GetValue()

    def set_value(self, val: str):
        self._controls['value'].SetValue(val)

    def enable(self, enabled: bool):
        self._controls['value'].Enable(enabled)

    def add(self, view: WxPythonView):
        self._children.append(view)

    def remove(self, view: WxPythonView):
        self._children.remove(view)

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        sizer = self._create_sizer()
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sub_sizer.Add(self._controls['num_elements'], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        sub_sizer.Add(self._controls['value'], border=5, flag=wx.ALL)
        sizer.Add(sub_sizer)

        content = wx.StaticBoxSizer(wx.VERTICAL, self._parent, self._name)
        for child in self._children:
            if recursive or not child._container:
                content.Add(child.get_sizer(recursive))
        sizer.Add(content)

        return sizer


class WxPythonChoiceView(WxPythonView, ChoiceView, ValueInterface):
    def __init__(self, name: str, controls: ControlList):
        super(WxPythonChoiceView, self).__init__(name, controls, True)
        self._view: Optional[WxPythonView] = None

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        self._controls['value'].Bind(wx.EVT_CHOICE, event_closure)

    def get_value(self) -> str:
        return self._controls['value'].GetStringSelection()

    def set_value(self, val: str):
        self._controls['value'].SetStringSelection(val)

    def enable(self, enabled: bool):
        self._controls['value'].Enable(enabled)
        if self._view is not None:
            self._view.enable(enabled)

    def set_view(self, view: WxPythonView):
        self._view = view

        if not self._controls['value'].Enabled:
            self._view.enable(False)

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer = self._create_sizer()
        sizer.Add(self._controls['value'], border=5)
        outer_sizer.Add(sizer)
        if recursive or not self._view._container:
            content_sizer = wx.BoxSizer(wx.VERTICAL)
            content_sizer.Add(self._view.get_sizer(recursive))
            outer_sizer.Add(content_sizer)

        return outer_sizer
