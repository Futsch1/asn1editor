import typing
from typing import Union, Optional, Callable, List, Tuple

import wx

from asn1editor.interfaces.BitstringInterface import BitstringInterface
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import AbstractView, ContainerView, ListView, ChoiceView


class WxPythonView(AbstractView, OptionalInterface):
    def __init__(self, sizer: wx.Sizer, optional_control: Optional[wx.CheckBox]):
        self._sizer = sizer
        self._optional_control = optional_control

    def register_optional_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()
            self._enable(self.get_has_value())

        if self._optional_control is not None:
            self._optional_control.Bind(wx.EVT_CHECKBOX, event_closure)

    def register_change_event(self, callback: Callable):
        pass

    def get_has_value(self) -> bool:
        if self._optional_control:
            return self._optional_control.GetValue()
        else:
            return True

    def set_has_value(self, val: bool):
        if self._optional_control:
            self._optional_control.SetValue(val)
            self._enable(val)

    def realize(self) -> wx.Sizer:
        return self._sizer

    def _enable(self, enabled: bool):
        raise NotImplementedError

    def destroy(self):
        self._sizer.Clear(True)


class WxPythonValueView(WxPythonView, ValueInterface):
    def __init__(self, sizer: wx.Sizer, value_control: Optional[Union[wx.TextCtrl, wx.ComboBox]] = None,
                 optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonValueView, self).__init__(sizer, optional_control)
        self._value_control = value_control

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        if self._value_control is not None:
            self._value_control.Bind(wx.EVT_TEXT, event_closure)

    def get_value(self) -> str:
        return self._value_control.GetValue()

    def set_value(self, val: str):
        self._value_control.SetValue(val)

    def _enable(self, enabled: bool):
        self._value_control.Enable(enabled)


class WxPythonHexStringView(WxPythonView, ValueInterface):
    class HexValidator(wx.Validator):
        def Clone(self):
            return WxPythonHexStringView.HexValidator()

        def Validate(self, parent):
            print(type(parent))

    def __init__(self, sizer: wx.Sizer, value_control: wx.TextCtrl, edit_selector: wx.RadioBox,
                 optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonHexStringView, self).__init__(sizer, optional_control)
        self._value_control = value_control
        self._value_control.SetValidator(self.HexValidator())
        self._edit_selector = edit_selector
        self._edit_selector.Bind(wx.EVT_RADIOBOX, self.edit_selector_changed)
        self._ascii = self._is_ascii()

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        if self._value_control is not None:
            self._value_control.Bind(wx.EVT_TEXT, event_closure)

    # noinspection PyUnusedLocal
    def edit_selector_changed(self, e: wx.CommandEvent):
        if self._ascii != self._is_ascii():
            val: str = self._value_control.GetValue()
            if self._ascii:
                val = val.encode('latin_1').hex()
            else:
                try:
                    val = bytes.fromhex(val).decode('latin_1')
                except ValueError:
                    e.Skip()
                    self._value_control.SetBackgroundColour(wx.YELLOW)
                    self._value_control.Update()
            self._value_control.SetValue(val)
            self._ascii = self._is_ascii()

    def get_value(self) -> str:
        val: str = self._value_control.GetValue()
        if self._is_ascii():
            return val
        else:
            return bytes.fromhex(val).decode('latin_1')

    def set_value(self, val: str):
        self._value_control.SetValue(val)

    def _enable(self, enabled: bool):
        self._value_control.Enable(enabled)

    def _is_ascii(self):
        selection = self._edit_selector.GetSelection()
        return self._edit_selector.GetString(selection) == 'ASCII'


class WxPythonBooleanView(WxPythonView, ValueInterface):
    def __init__(self, sizer: wx.Sizer, value_control: wx.CheckBox = None,
                 optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonBooleanView, self).__init__(sizer, optional_control)
        self._value_control = value_control

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        if self._value_control is not None:
            self._value_control.Bind(wx.EVT_CHECKBOX, event_closure)

    def get_value(self) -> str:
        return str(self._value_control.GetValue())

    def set_value(self, val: str):
        self._value_control.SetValue(val.lower() in ['true', '1'])

    def _enable(self, enabled: bool):
        self._value_control.Enable(enabled)


class WxPythonContainerView(WxPythonView, ContainerView):
    def __init__(self, sizer: wx.Sizer, container_sizer: wx.FlexGridSizer, optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonContainerView, self).__init__(sizer, optional_control)
        self._container_sizer = container_sizer
        self._children: List[wx.Sizer] = []

    def add_child(self, view: WxPythonView):
        self._children.append(view._sizer)
        self._container_sizer.Add(view._sizer)
        if not self.get_has_value():
            self._sizer.Hide(view._sizer, recursive=True)

    def _enable(self, enabled: bool):
        if enabled:
            for child in self._children:
                self._sizer.Show(child, recursive=True)
        else:
            for child in self._children:
                self._sizer.Hide(child, recursive=True)
        self._sizer.Layout()
        containing_window = self._sizer.GetContainingWindow()
        if containing_window is not None:
            self._sizer.GetContainingWindow().Layout()


class WxPythonListView(WxPythonView, ListView, ValueInterface):
    def __init__(self, sizer: wx.Sizer, num_control: wx.SpinCtrl, optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonListView, self).__init__(sizer, optional_control)
        self._num_control = num_control
        self._children: List[wx.Sizer] = []

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        self._num_control.Bind(wx.EVT_SPINCTRL, event_closure)

    def get_value(self) -> str:
        return self._num_control.GetValue()

    def set_value(self, val: str):
        self._num_control.SetValue(val)

    def _enable(self, enabled: bool):
        self._num_control.Enable(enabled)
        if enabled:
            for child in self._children:
                self._sizer.Show(child, recursive=True)
        else:
            for child in self._children:
                self._sizer.Hide(child, recursive=True)

    def add(self, view: WxPythonView):
        self._sizer.Add(view._sizer)
        self._sizer.Layout()
        self._children.append(view._sizer)

    def remove(self, view: WxPythonView):
        self._children.remove(view._sizer)
        view._sizer.Clear(True)
        self._sizer.Remove(view._sizer)
        self._sizer.Layout()


class WxPythonChoiceView(WxPythonView, ChoiceView, ValueInterface):
    def __init__(self, sizer: wx.Sizer, choice_control: wx.ComboBox, optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonChoiceView, self).__init__(sizer, optional_control)
        self._choice_control = choice_control
        self._view = None

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        self._choice_control.Bind(wx.EVT_TEXT, event_closure)

    def get_value(self) -> str:
        return self._choice_control.GetValue()

    def set_value(self, val: str):
        self._choice_control.SetValue(val)

    def _enable(self, enabled: bool):
        self._choice_control.Enable(enabled)

    def set_view(self, view: WxPythonView):
        if self._view is not None:
            self._view._sizer.Clear(True)
            self._sizer.Remove(self._view._sizer)
        self._sizer.Add(view._sizer)
        self._view = view
        self._sizer.Layout()


class WxPythonBitstringView(WxPythonView, BitstringInterface):
    def __init__(self, sizer: wx.Sizer, checkboxes: List[Tuple[int, wx.CheckBox]], optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonBitstringView, self).__init__(sizer, optional_control)
        self._checkboxes = checkboxes

    def _enable(self, enabled: bool):
        for _, checkbox in self._checkboxes:
            checkbox.Enable(enabled)

    def get_values(self) -> typing.List[int]:
        values = []
        for bit, checkbox in self._checkboxes:
            if checkbox.GetValue():
                values.append(bit)
        return values

    def set_values(self, values: typing.List[int]):
        for bit, checkbox in self._checkboxes:
            checkbox.SetValue(bit in values)
