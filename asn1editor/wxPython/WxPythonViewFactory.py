from typing import List, Tuple, Optional, Union

import wx
import wx.lib.masked.numctrl
import wx.svg

from asn1editor.interfaces.BitstringInterface import BitstringInterface
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import AbstractView, ContainerView, ListView, ChoiceView
from asn1editor.view.AbstractViewFactory import AbstractViewFactory
from asn1editor.wxPython.Resources import resource_path
from asn1editor.wxPython.Styler import Styler
from asn1editor.wxPython.WxPythonViews import WxPythonValueView, WxPythonView, WxPythonContainerView, WxPythonListView, WxPythonBooleanView, \
    WxPythonChoiceView, WxPythonBitstringView, WxPythonHexStringView, WxPythonValueSelectionView


class WxPythonViewFactory(AbstractViewFactory):
    def __init__(self, window: wx.ScrolledWindow, styler: Styler):
        self._window = window
        self._styler = styler

    def get_enumerated_view(self, name: str, choices: List[str], optional: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        optional_control = self._add_name_control(sizer, name, optional, ':', 'enumerated')
        edit = wx.Choice(self._window, choices=choices)
        sizer.Add(edit, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        style = self._styler.get_style(name)
        if style == 'read_only':
            edit.Enabled(False)
        if style == 'hidden':
            sizer.ShowItems(False)

        view = WxPythonValueSelectionView(sizer, edit, optional_control)
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
        sizer.Add(self._get_svg('sequence'))
        if optional:
            optional_control = self._add_name_control(sizer, name, optional)
        else:
            optional_control = None

        container_sizer = wx.FlexGridSizer(cols=2, vgap=8, hgap=8)
        sizer.Add(container_sizer)

        style = self._styler.get_style(name)
        if style == 'hidden':
            sizer.ShowItems(False)

        view = WxPythonContainerView(sizer, container_sizer, optional_control)

        return view, view if optional else None

    def get_list_view(self, name: str, minimum: int, maximum: int, optional: bool) -> Tuple[ListView, ValueInterface, OptionalInterface]:
        sizer = wx.StaticBoxSizer(wx.VERTICAL, self._window, name)
        sizer.Add(self._get_svg('sequence_of'))
        if optional:
            optional_control = self._add_name_control(sizer, name, optional)
        else:
            optional_control = None

        num_elements_sizer = wx.BoxSizer(wx.HORIZONTAL)
        num_elements_label = wx.StaticText(self._window, wx.ID_ANY, "Elements:")
        num_elements_sizer.Add(num_elements_label, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
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
        num_elements_sizer.Add(num_elements, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)

        content = wx.BoxSizer(wx.VERTICAL)
        content.Add(num_elements_sizer)

        sizer.Add(content)

        style = self._styler.get_style(name)
        if style == 'read_only':
            num_elements.Enabled(False)
        if style == 'hidden':
            sizer.ShowItems(False)

        view = WxPythonListView(sizer, num_elements, optional_control)

        return view, view, view if optional else None

    def get_number_view(self, name: str, optional: bool, minimum: Optional[Union[int, float]],
                        maximum: Optional[Union[int, float]], float_: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        optional_control = self._add_name_control(sizer, name, optional, ':', 'float' if float_ else 'integer')
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

        style = self._styler.get_style(name)
        if style == 'read_only':
            edit.SetEditable(False)
        if style == 'hidden':
            sizer.ShowItems(False)

        view = WxPythonValueView(sizer, edit, optional_control)
        return view, view, view if optional else None

    def get_boolean_view(self, name: str, optional: bool) -> Tuple[AbstractView, ValueInterface, OptionalInterface]:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        optional_control = self._add_name_control(sizer, name, optional, ':', 'bool')
        check_box = wx.CheckBox(self._window)
        sizer.Add(check_box, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        style = self._styler.get_style(name)
        if style == 'read_only':
            check_box.Enable(False)
        if style == 'hidden':
            sizer.ShowItems(False)

        view = WxPythonBooleanView(sizer, check_box, optional_control)
        return view, view, view if optional else None

    def get_string_view(self, name: str, string_type: str, optional: bool, minimum: Optional[int], maximum: Optional[int]):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        optional_control = self._add_name_control(sizer, name, optional, ':', 'string', string_type)
        edit = wx.TextCtrl(self._window)
        if maximum:
            edit.SetMaxLength(maximum)
        else:
            maximum = 'infinite'
        if minimum is None:
            minimum = '0'
        edit.SetToolTip(f"Minimum characters: {minimum}, maximum characters: {maximum}")

        sizer.Add(edit, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        style = self._styler.get_style(name)
        if style == 'read_only':
            edit.SetEditable(False)
        if style == 'hidden':
            sizer.ShowItems(False)

        view = WxPythonValueView(sizer, edit, optional_control)
        return view, view, view if optional else None

    def get_hex_string_view(self, name: str, optional: bool, minimum: Optional[int], maximum: Optional[int]):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        optional_control = self._add_name_control(sizer, name, optional, ':', 'string', 'OCTET STRING')
        selector = wx.CheckBox(self._window, label='Hex')
        sizer.Add(selector, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        edit = wx.TextCtrl(self._window)

        sizer.Add(edit, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        style = self._styler.get_style(name)
        if style == 'read_only':
            edit.SetEditable(False)
        if style == 'hidden':
            sizer.ShowItems(False)

        view = WxPythonHexStringView(sizer, edit, selector, minimum, maximum, optional_control)
        return view, view, view if optional else None

    def get_choice_view(self, name: str, choices: List[str], optional: bool) -> Tuple[ChoiceView, ValueInterface, OptionalInterface]:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        optional_control = self._add_name_control(sizer, name, optional, icon='choice')

        choice_element_sizer = wx.BoxSizer(wx.HORIZONTAL)
        choice_element_label = wx.StaticText(self._window, wx.ID_ANY)
        choice_element_sizer.Add(choice_element_label, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        choice_element = wx.Choice(self._window, choices=choices)
        choice_element_sizer.Add(choice_element, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)

        content = wx.BoxSizer(wx.VERTICAL)
        content.Add(choice_element_sizer)

        sizer.Add(content, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        style = self._styler.get_style(name)
        if style == 'read_only':
            choice_element.Enable(False)
        if style == 'hidden':
            sizer.ShowItems(False)

        view = WxPythonChoiceView(sizer, choice_element, optional_control)

        return view, view, view if optional else None

    def get_bitstring_view(self, name: str, number_of_bits: int, named_bits: List[Tuple[str, int]], optional: bool) -> Tuple[AbstractView, BitstringInterface,
                                                                                                                             OptionalInterface]:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        optional_control = self._add_name_control(sizer, name, optional, icon='bitstring')

        checkboxes: List[Tuple[int, wx.CheckBox]] = []

        style = self._styler.get_style(name)

        bits_sizer = wx.StaticBoxSizer(wx.VERTICAL, self._window, "Bits")
        if named_bits:
            for name, bit in named_bits:
                bit_checkbox = wx.CheckBox(self._window, label=f"{bit}: {name}")
                bits_sizer.Add(bit_checkbox)
                if style == 'read_only':
                    bit_checkbox.Enable(False)
                checkboxes.append((bit, bit_checkbox))
        else:
            for bit in range(number_of_bits):
                bit_checkbox = wx.CheckBox(self._window, label=str(bit))
                bits_sizer.Add(bit_checkbox)
                if style == 'read_only':
                    bit_checkbox.Enable(False)
                checkboxes.append((bit, bit_checkbox))

        sizer.Add(bits_sizer)

        if style == 'hidden':
            sizer.ShowItems(False)

        view = WxPythonBitstringView(sizer, checkboxes, optional_control)

        return view, view, view if optional else None

    def update(self):
        self._window.Layout()
        self._window.FitInside()
        self._window.AdjustScrollbars()

    def freeze(self):
        self._window.Freeze()

    def thaw(self):
        self._window.Thaw()

    def _add_name_control(self, sizer: wx.BoxSizer, name: str, optional: bool, suffix: str = '', icon: str = None, icon_tooltip: str = None) -> \
            Optional[wx.CheckBox]:
        flags = wx.ALL | (0 if sizer.GetOrientation() == wx.VERTICAL else wx.ALIGN_CENTER_VERTICAL)
        if optional:
            control = wx.CheckBox(self._window, wx.ID_ANY, name + suffix)
            control.SetToolTip("Optional element")
        else:
            control = wx.StaticText(self._window, wx.ID_ANY, name + suffix)
        if icon is not None:
            sizer.Add(self._get_svg(icon, icon_tooltip), flag=flags)
        sizer.Add(control, flag=flags, border=5)
        return control if optional else None

    def _get_svg(self, bitmap_name: str, icon_tooltip: str = None) -> wx.StaticBitmap:
        # noinspection PyArgumentList
        image: wx.svg.SVGimage = wx.svg.SVGimage.CreateFromFile(resource_path(f'icons/{bitmap_name}.svg'))
        bitmap = wx.StaticBitmap(self._window, bitmap=image.ConvertToBitmap(width=16, height=16))
        if icon_tooltip:
            bitmap.SetToolTip(icon_tooltip)
        else:
            bitmap.SetToolTip(bitmap_name.upper().replace('_', ' '))
        return bitmap
