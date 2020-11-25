from typing import List, Tuple, Optional, Union

import wx
import wx.lib.masked.numctrl
import wx.svg

from asn1editor.interfaces.BitstringInterface import BitstringInterface
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import AbstractView, ContainerView, ListView, ChoiceView
from asn1editor.view.AbstractViewFactory import AbstractViewFactory
from asn1editor.wxPython import Resources
from asn1editor.wxPython.Styler import Styler
from asn1editor.wxPython.WxPythonComplexViews import WxPythonContainerView, WxPythonListView, WxPythonChoiceView
from asn1editor.wxPython.WxPythonViews import WxPythonValueView, WxPythonBooleanView, \
    WxPythonBitstringView, WxPythonHexStringView, WxPythonValueSelectionView, ControlList


class WxPythonViewFactory(AbstractViewFactory):
    def __init__(self, window: wx.ScrolledWindow, styler: Styler):
        self._window = window
        self._styler = styler

    def get_enumerated_view(self, name: str, choices: List[str], optional: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(name, optional, ':', 'enumerated')

        controls['value'] = wx.ComboBox(self._window, choices=choices, style=wx.CB_READONLY)
        self._apply_style(controls)

        view = WxPythonValueSelectionView(name, controls)
        return view, view, view if optional else None

    def get_text_view(self, name: str, text: str) -> AbstractView:
        controls = self._get_controls(name, False)

        controls['value'] = wx.StaticText(self._window, wx.ID_ANY, text)
        self._apply_style(controls)

        view = WxPythonValueView(name, controls)

        return view

    def get_container_view(self, name: str, optional: bool) -> Tuple[ContainerView, OptionalInterface]:
        controls = self._get_controls(name, optional, icon=WxPythonContainerView.icon)

        view = WxPythonContainerView(name, controls, self._window)

        return view, view if optional else None

    def get_list_view(self, name: str, minimum: int, maximum: int, optional: bool) -> Tuple[ListView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(name, optional, icon=WxPythonListView.icon)

        num_elements = wx.SpinCtrl(self._window)
        if minimum is not None:
            num_elements.SetMin(minimum)
        else:
            minimum = 0
        if maximum is not None:
            num_elements.SetMax(maximum)
        else:
            maximum = 'infinite'
        num_elements.SetToolTip(f"Minimum elements: {minimum}, maximum elements: {maximum}")
        controls['value'] = num_elements
        controls['num_elements'] = wx.StaticText(self._window, wx.ID_ANY, "Elements:")
        self._apply_style(controls)

        view = WxPythonListView(name, controls, self._window)

        return view, view, view if optional else None

    def get_number_view(self, name: str, optional: bool, minimum: Optional[Union[int, float]],
                        maximum: Optional[Union[int, float]], float_: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(name, optional, ':', 'float' if float_ else 'integer')

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

        controls['value'] = edit
        self._apply_style(controls)

        view = WxPythonValueView(name, controls)
        return view, view, view if optional else None

    def get_boolean_view(self, name: str, optional: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(name, optional, ':', 'bool')

        controls['value'] = wx.CheckBox(self._window)
        self._apply_style(controls)

        view = WxPythonBooleanView(name, controls)
        return view, view, view if optional else None

    def get_string_view(self, name: str, string_type: str, optional: bool, minimum: Optional[int], maximum: Optional[int]):
        controls = self._get_controls(name, optional, ':', 'string', string_type)

        edit = wx.TextCtrl(self._window)
        if maximum:
            edit.SetMaxLength(maximum)
        else:
            maximum = 'infinite'
        if minimum is None:
            minimum = '0'
        edit.SetToolTip(f"Minimum characters: {minimum}, maximum characters: {maximum}")

        controls['value'] = edit
        self._apply_style(controls)

        view = WxPythonValueView(name, controls)
        return view, view, view if optional else None

    def get_hex_string_view(self, name: str, optional: bool, minimum: Optional[int], maximum: Optional[int]):
        controls = self._get_controls(name, optional, ':', 'string', 'OCTET STRING')

        controls['selector'] = wx.CheckBox(self._window, label='Hex')
        controls['value'] = wx.TextCtrl(self._window)
        self._apply_style(controls)

        view = WxPythonHexStringView(name, controls, minimum, maximum)
        return view, view, view if optional else None

    def get_choice_view(self, name: str, choices: List[str], optional: bool) -> Tuple[ChoiceView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(name, optional, icon=WxPythonChoiceView.icon)

        controls['value'] = wx.ComboBox(self._window, choices=choices, style=wx.CB_READONLY)
        self._apply_style(controls)

        view = WxPythonChoiceView(name, controls)

        return view, view, view if optional else None

    def get_bitstring_view(self, name: str, number_of_bits: int, named_bits: List[Tuple[str, int]], optional: bool) -> Tuple[AbstractView, BitstringInterface,
                                                                                                                             OptionalInterface]:
        controls = self._get_controls(name, optional, icon='bitstring')

        checkboxes: List[Tuple[int, wx.CheckBox]] = []

        style = self._styler.get_style(name)

        if named_bits:
            for name, bit in named_bits:
                bit_checkbox = wx.CheckBox(self._window, label=f"{bit}: {name}")
                if style == 'read_only':
                    bit_checkbox.Enable(False)
                checkboxes.append((bit, bit_checkbox))
        else:
            for bit in range(number_of_bits):
                bit_checkbox = wx.CheckBox(self._window, label=str(bit))
                if style == 'read_only':
                    bit_checkbox.Enable(False)
                checkboxes.append((bit, bit_checkbox))

        controls['checkboxes'] = checkboxes

        view = WxPythonBitstringView(name, controls, self._window)

        return view, view, view if optional else None

    def _get_controls(self, name: str, optional: bool, suffix: str = '', icon: str = None, icon_tooltip: str = None) -> \
            ControlList:
        controls = {}
        if optional:
            control = wx.CheckBox(self._window, wx.ID_ANY, name + suffix)
            control.SetToolTip("Optional element")
            controls['optional'] = control
            controls['name'] = control
        else:
            control = wx.StaticText(self._window, wx.ID_ANY, name + suffix)
            controls['name'] = control
        if icon is not None:
            controls['icon'] = self._get_svg(icon, icon_tooltip)

        style = self._styler.get_style(name)
        if style is not None:
            controls['style'] = style

        return controls

    def _get_svg(self, bitmap_name: str, icon_tooltip: str = None) -> wx.StaticBitmap:
        bitmap = Resources.image_list.get_bitmap(bitmap_name)
        if bitmap is None:
            bitmap = Resources.get_bitmap_from_svg(bitmap_name)

        static_bitmap = wx.StaticBitmap(self._window, bitmap=bitmap)

        if icon_tooltip:
            static_bitmap.SetToolTip(icon_tooltip)
        else:
            static_bitmap.SetToolTip(bitmap_name.upper().replace('_', ' '))
        return static_bitmap

    @staticmethod
    def _apply_style(controls: ControlList):
        if controls.get('style') == 'read_only' and 'value' in controls:
            controls['value'].Enable(False)
