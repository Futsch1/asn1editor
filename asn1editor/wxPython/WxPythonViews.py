import typing
from typing import Optional, Callable, List, Tuple

import wx

from asn1editor.interfaces.BitstringInterface import BitstringInterface
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractView import AbstractView

ControlList = typing.Dict[str, typing.Union[wx.TextCtrl, wx.CheckBox, wx.StaticBitmap, wx.ComboBox, wx.StaticText, wx.SpinCtrl, List[Tuple[int, wx.CheckBox]],
                                            str]]


class WxPythonView(AbstractView, OptionalInterface):
    structure_changed: Callable = None

    def __init__(self, name: str, controls: ControlList, container=False):
        self._name = name
        self._controls = controls
        self._container = container

    def register_optional_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            self._controls['optional'].GetTopLevelParent().Freeze()
            callback()
            self.enable(self.get_has_value())
            self._controls['optional'].GetTopLevelParent().Thaw()

        if 'optional' in self._controls:
            self._controls.get('optional').Bind(wx.EVT_CHECKBOX, event_closure)

    def register_change_event(self, callback: Callable):
        pass

    def get_has_value(self) -> bool:
        if 'optional' in self._controls:
            return self._controls.get('optional').GetValue()
        else:
            return True

    def set_has_value(self, val: bool):
        if 'optional' in self._controls:
            self._controls.get('optional').SetValue(val)
            self.enable(val)

    def realize(self) -> 'WxPythonView':
        return self

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        raise NotImplementedError()

    def enable(self, enabled: bool):
        return

    def destroy(self):
        for name, control in self._controls.items():
            if name == 'optional':
                continue
            if isinstance(control, wx.Object):
                control.Destroy()

    def get_name(self) -> str:
        return self._name

    def set_visible(self, visible, recursive=True):
        for control in self._controls.values():
            if isinstance(control, wx.Window):
                control.Show(visible)

    def _create_sizer(self, orientation: int = wx.HORIZONTAL) -> wx.BoxSizer:
        sizer = wx.BoxSizer(orientation)
        if orientation == wx.HORIZONTAL:
            if 'icon' in self._controls:
                sizer.Add(self._controls['icon'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
            sizer.Add(self._controls['name'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        else:
            if 'icon' in self._controls:
                sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
                sub_sizer.Add(self._controls['icon'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
                sub_sizer.Add(self._controls['name'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
                sizer.Add(sub_sizer)
            else:
                sizer.Add(self._controls['name'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)

        return sizer


class WxPythonValueView(WxPythonView, ValueInterface):
    def __init__(self, name: str, controls: ControlList):
        super(WxPythonValueView, self).__init__(name, controls)

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        sizer = self._create_sizer()
        sizer.Add(self._controls['value'], proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        if self._controls.get('style') == 'hidden':
            sizer.ShowItems(False)
        return sizer

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            self.__update_tooltip()
            callback()

        self._controls['value'].Bind(wx.EVT_TEXT, event_closure)

    def get_value(self) -> str:
        return self._controls['value'].GetValue()

    def set_value(self, val: str):
        self._controls['value'].SetValue(val)
        self.__update_tooltip()

    def enable(self, enabled: bool):
        self._controls['value'].Enable(enabled)

    def __update_tooltip(self):
        if isinstance(self.get_value(), str) and len(self.get_value()) > 10:
            tool_tip = self._controls['value'].GetToolTip()
            if tool_tip is not None:
                previous_tooltip = self._controls['value'].GetToolTip().GetTip().split('\n')
                previous_tooltip = previous_tooltip[-1]
            else:
                previous_tooltip = ''
            self._controls['value'].SetToolTip('\n'.join([self.get_value(), previous_tooltip]))


class WxPythonValueSelectionView(WxPythonView, ValueInterface):
    def __init__(self, name: str, controls: ControlList):
        super(WxPythonValueSelectionView, self).__init__(name, controls)

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        sizer = self._create_sizer()
        sizer.Add(self._controls['value'], flag=wx.ALL | wx.EXPAND, border=5)
        return sizer

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        self._controls['value'].Bind(wx.EVT_TEXT, event_closure)

    def get_value(self) -> str:
        return self._controls['value'].GetStringSelection()

    def set_value(self, val: str):
        self._controls['value'].SetStringSelection(val)

    def enable(self, enabled: bool):
        self._controls['value'].Enable(enabled)


class WxPythonHexStringView(WxPythonView, ValueInterface):
    def __init__(self, name: str, controls: ControlList, minimum: Optional[int], maximum: Optional[int]):
        super(WxPythonHexStringView, self).__init__(name, controls)

        self._real_value = b''
        self._controls['selector'].Bind(wx.EVT_CHECKBOX, self.hex_selector_changed)
        self._hex = self._is_hex()
        self._minimum = minimum
        if self._minimum is None:
            self._minimum = 0
        self._maximum = maximum
        self._update_length()

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        sizer = self._create_sizer()
        sizer.Add(self._controls['selector'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self._controls['value'], proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        return sizer

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            self.text_changed()
            callback()

        self._controls['value'].Bind(wx.EVT_TEXT, event_closure)

    # noinspection PyUnusedLocal
    def hex_selector_changed(self, e: wx.CommandEvent):
        self._hex_selector_changed()

    def text_changed(self):
        if self._hex:
            try:
                self._real_value = bytes.fromhex(self._controls['value'].GetValue())
            except ValueError:
                pass
        else:
            self._real_value = self._controls['value'].GetValue().encode('latin-1')

    def _update_control(self):
        if self._hex:
            val = self._real_value.hex()
            val = ' '.join(val[i:i + 2] for i in range(0, len(val), 2))
        else:
            val = self._real_value.decode('latin-1', errors='replace')

        self._controls['value'].ChangeValue(val)

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
            tool_tip = self._controls['value'].GetToolTip()
            if tool_tip is not None:
                previous_tooltip = self._controls['value'].GetToolTip().GetTip().split('\n')
                previous_tooltip = previous_tooltip[-1]
            else:
                previous_tooltip = ''
            self._controls['value'].SetToolTip('\n'.join([str(self.get_value()), previous_tooltip]))

    def get_value(self) -> bytes:
        return self._real_value

    def set_value(self, val: bytes):
        assert isinstance(val, bytes)
        self._real_value = val
        self._update_control()

    def enable(self, enabled: bool):
        self._controls['value'].Enable(enabled)

    def _is_hex(self) -> bool:
        return self._controls['selector'].GetValue()

    def _update_length(self):
        if self._maximum:
            self._controls['value'].SetToolTip(f"Minimum characters: {self._minimum}, maximum characters: {self._maximum}")
            self._controls['value'].SetMaxLength(self._maximum)


class WxPythonBooleanView(WxPythonView, ValueInterface):
    def __init__(self, name: str, controls: ControlList):
        super(WxPythonBooleanView, self).__init__(name, controls)

    def register_change_event(self, callback: Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        self._controls['value'].Bind(wx.EVT_CHECKBOX, event_closure)

    def get_value(self) -> bool:
        return self._controls['value'].GetValue()

    def set_value(self, val: bool):
        self._controls['value'].SetValue(val)

    def enable(self, enabled: bool):
        self._controls['value'].Enable(enabled)

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        sizer = self._create_sizer()
        sizer.Add(self._controls['value'], proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        return sizer


class WxPythonBitstringView(WxPythonView, BitstringInterface):
    def __init__(self, name: str, controls: ControlList, parent: wx.Window):
        super(WxPythonBitstringView, self).__init__(name, controls)
        self._parent = parent

    def enable(self, enabled: bool):
        for _, checkbox in self._controls['checkboxes']:
            checkbox.Enable(enabled)

    def get_values(self) -> typing.List[int]:
        values = []
        for bit, checkbox in self._controls['checkboxes']:
            if checkbox.GetValue():
                values.append(bit)
        return values

    def set_values(self, values: typing.List[int]):
        for bit, checkbox in self._controls['checkboxes']:
            checkbox.SetValue(bit in values)

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        sizer = self._create_sizer()
        bits_sizer = wx.StaticBoxSizer(wx.VERTICAL, self._parent, "Bits")
        for _, checkbox in self._controls['checkboxes']:
            bits_sizer.Add(checkbox)
        sizer.Add(bits_sizer)

        return sizer

    def destroy(self):
        super(WxPythonBitstringView, self).destroy()
        for _, checkbox in self._controls['checkboxes']:
            checkbox.Destroy()

    def set_visible(self, visible, recursive=True):
        super(WxPythonBitstringView, self).set_visible(visible, recursive)
        for _, checkbox in self._controls['checkboxes']:
            checkbox.Show(visible)
