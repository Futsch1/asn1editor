from typing import List, Tuple, Optional, Union

import wx
import wx.adv
import wx.lib.masked.numctrl
import wx.svg

from asn1editor.interfaces.BitstringInterface import BitstringInterface
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import AbstractView, ContainerView, ListView, ChoiceView
from asn1editor.view.AbstractViewFactory import AbstractViewFactory, TypeInfo, Styles
from asn1editor.wxPython import Resources
from asn1editor.wxPython.Labels import Labels
from asn1editor.wxPython.WxPythonComplexViews import WxPythonContainerView, WxPythonListView, WxPythonChoiceView
from asn1editor.wxPython.WxPythonDateTimeViews import WxPythonDateView, WxPythonTimeView, WxPythonDateTimeView
from asn1editor.wxPython.WxPythonViews import WxPythonValueView, WxPythonBooleanView, \
    WxPythonBitstringView, WxPythonHexStringView, WxPythonValueSelectionView, ControlList


class WxPythonViewFactory(AbstractViewFactory):
    def __init__(self, window: wx.ScrolledWindow, labels: Labels):
        self._window = window
        self._labels = labels

    def get_enumerated_view(self, type_info: TypeInfo, choices: List[str]) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(type_info, ':', 'enumerated')

        controls['value'] = wx.ComboBox(self._window, choices=choices, style=wx.CB_READONLY)
        self._apply_style(controls)

        view = WxPythonValueSelectionView(type_info, controls)
        return view, view, view if type_info.optional or type_info.additional else None

    def get_text_view(self, type_info: TypeInfo, text: str) -> AbstractView:
        controls = self._get_controls(type_info)

        controls['value'] = wx.StaticText(self._window, wx.ID_ANY, text)
        self._apply_style(controls)

        view = WxPythonValueView(type_info, controls)

        return view

    def get_container_view(self, type_info: TypeInfo) -> Tuple[ContainerView, OptionalInterface]:
        controls = self._get_controls(type_info, icon=WxPythonContainerView.icon)

        view = WxPythonContainerView(type_info, controls, self._window)

        return view, view if type_info.optional or type_info.additional else None

    def get_list_view(self, type_info: TypeInfo, minimum: int, maximum: int) -> Tuple[ListView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(type_info, icon=WxPythonListView.icon)

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

        view = WxPythonListView(type_info, controls, self._window)

        return view, view, view if type_info.optional or type_info.additional else None

    def get_number_view(self, type_info: TypeInfo, minimum: Optional[Union[int, float]],
                        maximum: Optional[Union[int, float]], float_: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(type_info, ':', 'float' if float_ else 'integer')

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

        view = WxPythonValueView(type_info, controls)
        return view, view, view if type_info.optional or type_info.additional else None

    def get_boolean_view(self, type_info: TypeInfo) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(type_info, ':', 'bool')

        controls['value'] = wx.CheckBox(self._window)
        self._apply_style(controls)

        view = WxPythonBooleanView(type_info, controls)
        return view, view, view if type_info.optional or type_info.additional else None

    def get_string_view(self, type_info: TypeInfo, minimum: Optional[int], maximum: Optional[int]):
        controls = self._get_controls(type_info, ':', 'string')

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

        view = WxPythonValueView(type_info, controls)
        return view, view, view if type_info.optional or type_info.additional else None

    def get_hex_string_view(self, type_info: TypeInfo, minimum: Optional[int], maximum: Optional[int]):
        controls = self._get_controls(type_info, ':', 'string')

        controls['selector'] = wx.CheckBox(self._window, label='Hex')
        controls['selector'].SetValue(True)
        controls['value'] = wx.TextCtrl(self._window)
        self._apply_style(controls)

        view = WxPythonHexStringView(type_info, controls, minimum, maximum)
        return view, view, view if type_info.optional else None

    def get_choice_view(self, type_info: TypeInfo, choices: List[str]) -> Tuple[ChoiceView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(type_info, icon=WxPythonChoiceView.icon)

        controls['value'] = wx.ComboBox(self._window, choices=choices, style=wx.CB_READONLY)
        self._apply_style(controls)

        view = WxPythonChoiceView(type_info, controls)

        return view, view, view if type_info.optional or type_info.additional else None

    def get_bitstring_view(self, type_info: TypeInfo, number_of_bits: int, named_bits: List[Tuple[str, int]]) -> \
            Tuple[AbstractView, BitstringInterface, OptionalInterface]:
        controls = self._get_controls(type_info, icon='bitstring')

        checkboxes: List[Tuple[int, wx.CheckBox]] = []

        style = type_info.style

        if named_bits:
            for name, bit in named_bits:
                bit_checkbox = wx.CheckBox(self._window, label=f"{bit}: {name}")
                if style & Styles.READ_ONLY:
                    bit_checkbox.Enable(False)
                checkboxes.append((bit, bit_checkbox))
        else:
            for bit in range(number_of_bits):
                bit_checkbox = wx.CheckBox(self._window, label=str(bit))
                if style & Styles.READ_ONLY:
                    bit_checkbox.Enable(False)
                checkboxes.append((bit, bit_checkbox))

        controls['checkboxes'] = checkboxes

        view = WxPythonBitstringView(type_info, controls, self._window)

        return view, view, view if type_info.optional or type_info.additional else None

    def get_date_view(self, type_info: TypeInfo) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(type_info, ':', 'date')

        controls['value'] = wx.adv.DatePickerCtrl(self._window)
        self._apply_style(controls)

        view = WxPythonDateView(type_info, controls)
        return view, view, view if type_info.optional or type_info.additional else None

    def get_time_view(self, type_info: TypeInfo) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(type_info, ':', 'date')

        controls['value'] = wx.adv.TimePickerCtrl(self._window)
        self._apply_style(controls)

        view = WxPythonTimeView(type_info, controls)
        return view, view, view if type_info.optional else None

    def get_datetime_view(self, type_info: TypeInfo) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        controls = self._get_controls(type_info, ':', 'date')

        controls['value'] = wx.adv.DatePickerCtrl(self._window)
        controls['time'] = wx.adv.TimePickerCtrl(self._window)
        self._apply_style(controls)

        view = WxPythonDateTimeView(type_info, controls)
        return view, view, view if type_info.optional or type_info.additional else None

    def _get_controls(self, type_info: TypeInfo, suffix: str = '', icon: str = None) -> ControlList:
        controls = {}

        label = self._labels.get_label(type_info, suffix)
        tooltip = self._labels.get_tooltip(type_info)

        if type_info.optional or type_info.additional:
            control = wx.CheckBox(self._window, wx.ID_ANY, label)
            if type_info.additional and not type_info.optional:
                control.Enable(False)
            controls['optional'] = control
        else:
            control = wx.StaticText(self._window, wx.ID_ANY, label)

        controls['name'] = control
        control.SetToolTip(tooltip)
        if icon is not None:
            controls['icon'] = self._get_svg(icon, tooltip)

        if type_info.style is not None:
            controls['style'] = type_info.style
        else:
            controls['style'] = 0

        return controls

    def _get_svg(self, bitmap_name: str, icon_tooltip: str = None) -> wx.StaticBitmap:
        bitmap = Resources.image_list.get_bitmap(bitmap_name)
        if bitmap is None:
            bitmap = Resources.get_bitmap_from_svg(bitmap_name)

        static_bitmap = wx.StaticBitmap(self._window, bitmap=bitmap)

        static_bitmap.SetToolTip(icon_tooltip)
        return static_bitmap

    @staticmethod
    def _apply_style(controls: ControlList):
        if controls.get('style') & Styles.READ_ONLY and 'value' in controls:
            controls['value'].Enable(False)
