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

        if self.get_has_value():
            sizer.Add(self._controls['icon'], flag=wx.ALL)

            if recursive:
                container_sizer = wx.FlexGridSizer(cols=2, vgap=8, hgap=8)
                sizer.Add(container_sizer)
            else:
                container_sizer = sizer

            for child in self._children:
                if recursive or not child._container:
                    container_sizer.Add(child.get_sizer(recursive))

        return sizer

    def add_child(self, view: WxPythonView):
        if self.any_shown(view.get_sizer(False)):
            self._children.append(view)

    def enable(self, enabled: bool):
        pass

    def get_children(self) -> List[WxPythonView]:
        return self._children

    @staticmethod
    def any_shown(sizer: wx.Sizer) -> bool:
        return any([child.IsShown() for child in sizer.GetChildren()])


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
        sub_sizer.Add(self._controls['num_elements'], border=5)
        sub_sizer.Add(self._controls['value'], border=5)
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
