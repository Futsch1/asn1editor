import typing

import wx

from asn1editor.interfaces.BitstringInterface import BitstringInterface
from asn1editor.view.AbstractViewFactory import TypeInfo
from asn1editor.wxPython.views.WxPythonView import WxPythonView, ControlList


class WxPythonBitstringView(WxPythonView, BitstringInterface):
    def __init__(self, type_info: TypeInfo, controls: ControlList, parent: wx.Window):
        super(WxPythonBitstringView, self).__init__(type_info, controls)
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

    def get_sizers(self, recursive: bool) -> typing.Tuple[wx.Sizer, typing.Optional[wx.Sizer]]:
        sizer = self._create_sizer()
        if self._controls['name'].IsShown():
            bits_sizer = wx.StaticBoxSizer(wx.VERTICAL, self._parent, "Bits")
        else:
            bits_sizer = wx.BoxSizer(wx.VERTICAL)

        for _, checkbox in self._controls['checkboxes']:
            bits_sizer.Add(checkbox, border=5)

        return sizer, bits_sizer

    def destroy(self):
        super(WxPythonBitstringView, self).destroy()
        for _, checkbox in self._controls['checkboxes']:
            checkbox.Destroy()

    def set_visible(self, visible, recursive=True):
        super(WxPythonBitstringView, self).set_visible(visible, recursive)
        for _, checkbox in self._controls['checkboxes']:
            checkbox.Show(visible)
