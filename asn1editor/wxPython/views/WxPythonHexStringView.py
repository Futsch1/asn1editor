import typing

import wx

from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractViewFactory import TypeInfo
from asn1editor.wxPython.views.WxPythonView import WxPythonView, ControlList


class WxPythonHexStringView(WxPythonView, ValueInterface):
    CHARS_PER_HEX_DIGIT = 3

    def __init__(self, type_info: TypeInfo, controls: ControlList, minimum: typing.Optional[int], maximum: typing.Optional[int]):
        super(WxPythonHexStringView, self).__init__(type_info, controls)

        self._real_value = b''
        self._controls['selector'].Bind(wx.EVT_CHECKBOX, self.hex_selector_changed)
        self._hex = self._is_hex()
        self._minimum = minimum if not self._hex or minimum is None else minimum * self.CHARS_PER_HEX_DIGIT
        if self._minimum is None:
            self._minimum = 0
        self._maximum = maximum if not self._hex or maximum is None else maximum * self.CHARS_PER_HEX_DIGIT
        self._update_length()

    def get_sizers(self, recursive: bool) -> typing.Tuple[wx.Sizer, typing.Optional[wx.Sizer]]:
        sizer = self._create_sizer()
        value_sizer = wx.BoxSizer(wx.HORIZONTAL)
        value_sizer.Add(self._controls['selector'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        value_sizer.Add(self._controls['value'], proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        return sizer, value_sizer

    def register_change_event(self, callback: typing.Callable):
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
                    self._maximum *= self.CHARS_PER_HEX_DIGIT
                self._minimum *= self.CHARS_PER_HEX_DIGIT
            else:
                if self._maximum:
                    self._maximum //= self.CHARS_PER_HEX_DIGIT
                self._minimum //= self.CHARS_PER_HEX_DIGIT

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
