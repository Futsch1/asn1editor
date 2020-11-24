from typing import Optional, List, Callable

import wx

from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import ContainerView, ListView, ChoiceView
from asn1editor.wxPython.WxPythonViews import WxPythonView, ControlList


class WxPythonContainerView(WxPythonView, ContainerView):
    icon = 'sequence'

    def __init__(self, name: str, controls: ControlList, parent: wx.Window):
        super(WxPythonContainerView, self).__init__(name, controls, container=True)
        self._children: List[WxPythonView] = []
        self._parent = parent

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        if recursive and self.get_has_value() and self._controls['name'].IsShown():
            sizer = wx.StaticBoxSizer(wx.VERTICAL, self._parent, self._name)
        else:
            sizer = wx.BoxSizer(wx.VERTICAL)

        if 'optional' not in self._controls:
            self._controls['icon'].Show(False)
            self._controls['name'].Show(False)
        else:
            name_sizer = wx.BoxSizer(wx.HORIZONTAL)
            name_sizer.Add(self._controls['icon'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
            name_sizer.Add(self._controls['name'], flag=wx.ALL, border=5)
            sizer.Add(name_sizer)

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
        self._children.append(view)
        view.set_visible(self.get_has_value(), recursive=True)

    def enable(self, enabled: bool):
        for child in self._children:
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
            if recursive or not child._container:
                child.set_visible(visible and self.get_has_value(), recursive)


class WxPythonListView(WxPythonContainerView, ListView, ValueInterface):
    icon = 'sequence_of'

    def __init__(self, name: str, controls: ControlList, parent: wx.Window):
        super(WxPythonListView, self).__init__(name, controls, parent)

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

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        sizer = self._create_sizer(wx.VERTICAL)
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sub_sizer.Add(self._controls['num_elements'], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        sub_sizer.Add(self._controls['value'], border=5, flag=wx.ALL)
        sizer.Add(sub_sizer)

        if recursive and self.get_has_value() and self._controls['name'].IsShown():
            content = wx.StaticBoxSizer(wx.VERTICAL, self._parent, self._name)
        else:
            content = wx.BoxSizer(wx.VERTICAL)
        for child in self._children:
            if recursive or not child._container:
                child_sizer = child.get_sizer(recursive)
                content.Add(child_sizer)
        sizer.Add(content)

        return sizer


class WxPythonChoiceView(WxPythonView, ChoiceView, ValueInterface):
    icon = 'choice'

    def __init__(self, name: str, controls: ControlList):
        super(WxPythonChoiceView, self).__init__(name, controls, True)
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

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer = self._create_sizer(wx.VERTICAL)
        sizer.Add(self._controls['value'], border=5)
        outer_sizer.Add(sizer)
        if recursive or not self._view._container:
            content_sizer = wx.BoxSizer(wx.VERTICAL)
            view_sizer = self._view.get_sizer(recursive)
            content_sizer.Add(view_sizer)
            if not self.get_has_value():
                content_sizer.Hide(view_sizer)
            outer_sizer.Add(content_sizer)

        return outer_sizer

    def destroy(self):
        super(WxPythonChoiceView, self).destroy()
        if self._view is not None:
            self._view.destroy()

    def set_visible(self, visible, recursive=True):
        super(WxPythonChoiceView, self).set_visible(visible, recursive)
        if recursive or not self._view._container:
            self._view.set_visible(visible and self.get_has_value(), recursive)
