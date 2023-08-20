import typing
from typing import Optional, List, Callable

import wx

from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import ContainerView, ListView, ChoiceView
from asn1editor.view.AbstractViewFactory import TypeInfo
from asn1editor.wxPython.WxPythonViews import WxPythonView, ControlList


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
