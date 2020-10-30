import typing
from typing import Optional, Callable, List, Tuple

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
            self.enable(self.get_has_value())

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
            self.enable(val)

    def realize(self) -> wx.Sizer:
        return self._sizer

    def enable(self, enabled: bool):
        return

    def destroy(self):
        self._sizer.Clear(True)


class WxPythonValueView(WxPythonView, ValueInterface):
    def __init__(self, sizer: wx.Sizer, value_control: Optional[wx.TextCtrl] = None,
                 optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonValueView, self).__init__(sizer, optional_control)
        self._value_control = value_control

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            self.__update_tooltip()
            callback()

        if self._value_control is not None:
            self._value_control.Bind(wx.EVT_TEXT, event_closure)

    def get_value(self) -> str:
        return self._value_control.GetValue()

    def set_value(self, val: str):
        self._value_control.SetValue(val)
        self.__update_tooltip()

    def enable(self, enabled: bool):
        self._value_control.Enable(enabled)

    def __update_tooltip(self):
        if isinstance(self.get_value(), str) and len(self.get_value()) > 10:
            tool_tip = self._value_control.GetToolTip()
            if tool_tip is not None:
                previous_tooltip = self._value_control.GetToolTip().GetTip().split('\n')
                previous_tooltip = previous_tooltip[-1]
            else:
                previous_tooltip = ''
            self._value_control.SetToolTip('\n'.join([self.get_value(), previous_tooltip]))


class WxPythonValueSelectionView(WxPythonView, ValueInterface):
    def __init__(self, sizer: wx.Sizer, value_control: Optional[wx.Choice] = None,
                 optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonValueSelectionView, self).__init__(sizer, optional_control)
        self._value_control = value_control

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        if self._value_control is not None:
            self._value_control.Bind(wx.EVT_CHOICE, event_closure)

    def get_value(self) -> str:
        return self._value_control.GetStringSelection()

    def set_value(self, val: str):
        self._value_control.SetStringSelection(val)

    def enable(self, enabled: bool):
        self._value_control.Enable(enabled)


class WxPythonHexStringView(WxPythonView, ValueInterface):
    def __init__(self, sizer: wx.Sizer, value_control: wx.TextCtrl, hex_selector: wx.CheckBox, minimum: Optional[int], maximum: Optional[int],
                 optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonHexStringView, self).__init__(sizer, optional_control)

        self._value_control = value_control
        self._real_value = b''
        self._hex_selector = hex_selector
        self._hex_selector.Bind(wx.EVT_CHECKBOX, self.hex_selector_changed)
        self._hex = self._is_hex()
        self._minimum = minimum
        if self._minimum is None:
            self._minimum = 0
        self._maximum = maximum
        self._update_length()

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            self.text_changed()
            callback()

        if self._value_control is not None:
            self._value_control.Bind(wx.EVT_TEXT, event_closure)

    # noinspection PyUnusedLocal
    def hex_selector_changed(self, e: wx.CommandEvent):
        self._hex_selector_changed()

    def text_changed(self):
        if self._hex:
            try:
                self._real_value = bytes.fromhex(self._value_control.GetValue())
            except ValueError:
                pass
        else:
            self._real_value = self._value_control.GetValue().encode('latin-1')

    def _update_control(self):
        if self._hex:
            val = self._real_value.hex()
            val = ' '.join(val[i:i + 2] for i in range(0, len(val), 2))
        else:
            val = self._real_value.decode('latin-1', errors='replace')

        self._value_control.ChangeValue(val)

        self.__update_tooltip()

    def _hex_selector_changed(self):
        if self._hex != self._is_hex():
            if not self._hex:
                # Was ASCII before, now is hex
                if self._maximum:
                    self._maximum *= 2
                self._minimum *= 2
            else:
                if self._maximum:
                    self._maximum //= 2
                self._minimum //= 2

            self._update_length()
            self._hex = self._is_hex()
            self._update_control()

    def __update_tooltip(self):
        if len(self.get_value()) > 10:
            tool_tip = self._value_control.GetToolTip()
            if tool_tip is not None:
                previous_tooltip = self._value_control.GetToolTip().GetTip().split('\n')
                previous_tooltip = previous_tooltip[-1]
            else:
                previous_tooltip = ''
            self._value_control.SetToolTip('\n'.join([str(self.get_value()), previous_tooltip]))

    def get_value(self) -> bytes:
        return self._real_value

    def set_value(self, val: bytes):
        assert isinstance(val, bytes)
        self._real_value = val
        self._update_control()

    def enable(self, enabled: bool):
        self._value_control.Enable(enabled)

    def _is_hex(self) -> bool:
        return self._hex_selector.GetValue()

    def _update_length(self):
        if self._maximum:
            self._value_control.SetToolTip(f"Minimum characters: {self._minimum}, maximum characters: {self._maximum}")
            self._value_control.SetMaxLength(self._maximum)


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

    def get_value(self) -> bool:
        return self._value_control.GetValue()

    def set_value(self, val: bool):
        self._value_control.SetValue(val)

    def enable(self, enabled: bool):
        self._value_control.Enable(enabled)


class WxPythonContainerView(WxPythonView, ContainerView):
    def __init__(self, sizer: wx.Sizer, container_sizer: wx.FlexGridSizer, optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonContainerView, self).__init__(sizer, optional_control)
        self._container_sizer = container_sizer
        self._children: List[wx.Sizer] = []

    def add_child(self, view: WxPythonView):
        if self.any_shown(view._sizer):
            self._children.append(view._sizer)
            self._container_sizer.Add(view._sizer)
            if not self.get_has_value():
                self._sizer.Hide(view._sizer, recursive=True)

    def enable(self, enabled: bool):
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

    @staticmethod
    def any_shown(sizer: wx.Sizer) -> bool:
        return any([child.IsShown() for child in sizer.GetChildren()])


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

    def enable(self, enabled: bool):
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
    def __init__(self, sizer: wx.Sizer, choice_control: wx.Choice, optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonChoiceView, self).__init__(sizer, optional_control)
        self._choice_control = choice_control
        self._view = None

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        self._choice_control.Bind(wx.EVT_CHOICE, event_closure)

    def get_value(self) -> str:
        return self._choice_control.GetStringSelection()

    def set_value(self, val: str):
        self._choice_control.SetStringSelection(val)

    def enable(self, enabled: bool):
        self._choice_control.Enable(enabled)
        if self._view is not None:
            self._view.enable(enabled)

    def set_view(self, view: WxPythonView):
        if self._view is not None:
            self._view._sizer.Clear(True)
            self._sizer.Remove(self._view._sizer)
        self._sizer.Add(view._sizer)
        self._view = view
        self._sizer.Layout()

        if not self._choice_control.Enabled:
            self._view.enable(False)


class WxPythonBitstringView(WxPythonView, BitstringInterface):
    def __init__(self, sizer: wx.Sizer, checkboxes: List[Tuple[int, wx.CheckBox]], optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonBitstringView, self).__init__(sizer, optional_control)
        self._checkboxes = checkboxes

    def enable(self, enabled: bool):
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
