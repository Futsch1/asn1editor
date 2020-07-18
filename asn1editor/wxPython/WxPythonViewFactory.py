from typing import List, Tuple, Optional, Union

import wx
import wx.lib.masked.numctrl

from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import AbstractView, ContainerView, ListView, ChoiceView
from asn1editor.view.AbstractViewFactory import AbstractViewFactory
from asn1editor.wxPython.WxPythonViews import WxPythonValueView, WxPythonView, WxPythonContainerView, WxPythonListView, WxPythonBooleanView, WxPythonChoiceView


class WxPythonViewFactory(AbstractViewFactory):
    def __init__(self, window: wx.Window):
        self._window = window

    def get_enumerated_view(self, name: str, choices: List[str], optional: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        optional_control = self._add_name_control(sizer, name, optional, ':')
        edit = wx.ComboBox(self._window, style=wx.CB_DROPDOWN, choices=choices)
        sizer.Add(edit, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        view = WxPythonValueView(sizer, edit, optional_control)
        return view, view, view if optional else None

    def get_text_view(self, name: str, text: str) -> AbstractView:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        dummy_text = wx.StaticText(self._window, wx.ID_ANY, text)
        self._add_name_control(sizer, name, False)
        sizer.Add(dummy_text, flag=wx.ALL, border=5)

        view = WxPythonView(sizer, None)

        return view

    def get_container_view(self, name: str, optional: bool) -> Tuple[ContainerView, OptionalInterface]:
        sizer = wx.StaticBoxSizer(wx.VERTICAL, self._window, name)
        if optional:
            optional_control = self._add_name_control(sizer, name, optional)
        else:
            optional_control = None

        container_sizer = wx.FlexGridSizer(2, 5, 5)
        sizer.Add(container_sizer)

        view = WxPythonContainerView(sizer, container_sizer, optional_control)

        return view, view if optional else None

    def get_list_view(self, name: str, minimum: int, maximum: int, optional: bool) -> Tuple[ListView, ValueInterface, OptionalInterface]:
        sizer = wx.StaticBoxSizer(wx.VERTICAL, self._window, name)
        if optional:
            optional_control = self._add_name_control(sizer, name, optional)
        else:
            optional_control = None

        num_elements_sizer = wx.BoxSizer(wx.HORIZONTAL)
        num_elements_label = wx.StaticText(self._window, wx.ID_ANY, "Elements:")
        num_elements_sizer.Add(num_elements_label, flag=wx.ALL, border=5)
        num_elements = wx.SpinCtrl(self._window)
        num_elements.SetMin(minimum)
        num_elements.SetMax(maximum)
        num_elements.SetToolTip(f"Minimum elements: {minimum}, maximum elements: {maximum}")
        num_elements_sizer.Add(num_elements, flag=wx.ALL, border=5)

        content = wx.BoxSizer(wx.VERTICAL)
        content.Add(num_elements_sizer)

        sizer.Add(content)

        view = WxPythonListView(sizer, num_elements, optional_control)

        return view, view, view if optional else None

    def get_number_view(self, name: str, optional: bool, minimum: Optional[Union[int, float]],
                        maximum: Optional[Union[int, float]], float_: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        optional_control = self._add_name_control(sizer, name, optional, ':')
        edit = wx.lib.masked.numctrl.NumCtrl(self._window)
        tool_tip = []
        if isinstance(minimum, int) or isinstance(minimum, float):
            edit.SetAllowNegative(minimum < 0)
            edit.SetMin(minimum)
            tool_tip.append(f'Minimum: {minimum}')
        if isinstance(maximum, int) or isinstance(maximum, float):
            edit.SetMax(maximum)
            tool_tip.append(f'Maximum: {maximum}')
        if float_:
            edit.SetFractionWidth(6)
        if len(tool_tip):
            edit.SetToolTip(', '.join(tool_tip))
        sizer.Add(edit, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        view = WxPythonValueView(sizer, edit, optional_control)
        return view, view, view if optional else None

    def get_boolean_view(self, name: str, optional: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        optional_control = self._add_name_control(sizer, name, optional, ':')
        check_box = wx.CheckBox(self._window)
        sizer.Add(check_box, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        view = WxPythonBooleanView(sizer, check_box, optional_control)
        return view, view, view if optional else None

    def get_string_view(self, name: str, optional: bool, minimum: int, maximum: int):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        optional_control = self._add_name_control(sizer, name, optional, ':')
        edit = wx.TextCtrl(self._window)
        edit.SetToolTip(f"Minimum characters: {minimum}, maximum characters: {maximum}")
        edit.SetMaxLength(maximum)

        sizer.Add(edit, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        view = WxPythonValueView(sizer, edit, optional_control)
        return view, view, view if optional else None

    def get_choice_view(self, name: str, choices: List[str], optional: bool) -> Tuple[ChoiceView, ValueInterface, OptionalInterface]:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        optional_control = self._add_name_control(sizer, name, optional)

        choice_element_sizer = wx.BoxSizer(wx.HORIZONTAL)
        choice_element_label = wx.StaticText(self._window, wx.ID_ANY)
        choice_element_sizer.Add(choice_element_label, flag=wx.ALL, border=5)
        choice_element = wx.ComboBox(self._window, style=wx.CB_DROPDOWN, choices=choices)
        choice_element_sizer.Add(choice_element, flag=wx.ALL, border=5)

        content = wx.BoxSizer(wx.VERTICAL)
        content.Add(choice_element_sizer)

        sizer.Add(content)

        view = WxPythonChoiceView(sizer, choice_element, optional_control)

        return view, view, view if optional else None

    def update(self):
        self._window.Layout()

    def freeze(self):
        self._window.Freeze()

    def thaw(self):
        self._window.Thaw()

    def _add_name_control(self, sizer: wx.Sizer, name: str, optional: bool, suffix: str = '') -> Optional[wx.CheckBox]:
        if optional:
            control = wx.CheckBox(self._window, wx.ID_ANY, name + suffix)
            control.SetToolTip("Optional element")
        else:
            control = wx.StaticText(self._window, wx.ID_ANY, name + suffix)
        sizer.Add(control, flag=wx.ALL, border=5)
        return control if optional else None
