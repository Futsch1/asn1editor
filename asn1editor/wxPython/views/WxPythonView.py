import typing

import wx
import wx.adv

import asn1editor.view
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.view.AbstractView import AbstractView
from asn1editor.view.AbstractViewFactory import TypeInfo

# @formatter:off
ControlList = typing.Dict[str,
                          typing.Union[wx.TextCtrl, wx.CheckBox, wx.StaticBitmap, wx.ComboBox, wx.StaticText, wx.SpinCtrl,
                                       typing.List[typing.Tuple[int, wx.CheckBox]], asn1editor.view.AbstractViewFactory.Styles,
                                       wx.adv.DatePickerCtrl, wx.adv.TimePickerCtrl]]
# @formatter:on


class WxPythonView(AbstractView, OptionalInterface):
    structure_changed: typing.Callable = None

    def __init__(self, type_info: TypeInfo, controls: ControlList, container=False):
        self._type_info = type_info
        self._controls = controls
        self.container = container

    def register_optional_event(self, callback: typing.Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            self._controls['optional'].GetTopLevelParent().Freeze()
            callback()
            self.enable(self.get_has_value())
            self._controls['optional'].GetTopLevelParent().Thaw()

        if 'optional' in self._controls:
            self._controls.get('optional').Bind(wx.EVT_CHECKBOX, event_closure)

    def register_change_event(self, callback: typing.Callable):
        pass

    def get_has_value(self) -> bool:
        if 'optional' in self._controls and (not self._type_info.additional or self._type_info.optional):
            return self._controls.get('optional').GetValue()
        else:
            return True

    def set_has_value(self, val: bool):
        if 'optional' in self._controls:
            self._controls.get('optional').SetValue(val)
            if not self._type_info.additional or self._type_info.optional:
                self.enable(val)

    def get_default_has_value(self) -> bool:
        return not self._type_info.optional

    def realize(self) -> 'WxPythonView':
        return self

    def get_sizers(self, recursive: bool) -> typing.Tuple[wx.Sizer, typing.Optional[wx.Sizer]]:
        raise NotImplementedError()

    def enable(self, enabled: bool):
        return

    def destroy(self):
        for name, control in self._controls.items():
            if name == 'optional':
                continue
            if isinstance(control, wx.Object):
                control.Destroy()

    def get_type_info(self) -> TypeInfo:
        return self._type_info

    def set_visible(self, visible, recursive=True):
        for control in self._controls.values():
            if isinstance(control, wx.Window):
                control.Show(visible)

    def _create_sizer(self, orientation: int = wx.HORIZONTAL) -> wx.BoxSizer:
        sizer = wx.BoxSizer(orientation)
        if orientation == wx.HORIZONTAL:
            if 'icon' in self._controls:
                sizer.Add(self._controls['icon'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=2)
            sizer.Add(self._controls['name'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        else:
            if 'icon' in self._controls:
                sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
                sub_sizer.Add(self._controls['icon'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=2)
                sub_sizer.Add(self._controls['name'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
                sizer.Add(sub_sizer)
            else:
                sizer.Add(self._controls['name'], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)

        return sizer

    @staticmethod
    def _get_container_sizer(recursive: bool, children: typing.List['WxPythonView']) -> wx.GridBagSizer:
        container_sizer = wx.GridBagSizer(5, 15)

        children = list(filter(lambda c: recursive or not c.container, children))

        for index, child in enumerate(children):
            left_column = index < len(children) // 2
            column = 0 if left_column else 2
            row = index if left_column else index - len(children) // 2

            left_column_sizer, right_column_sizer = child.get_sizers(recursive)
            gb_left_pos = wx.GBPosition(row, column)
            # If no right column present, span over two columns
            if right_column_sizer is None:
                gb_left_span = wx.GBSpan(1, 2)
            else:
                gb_left_span = wx.GBSpan()

            container_sizer.Add(left_column_sizer, gb_left_pos, gb_left_span, flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)

            if right_column_sizer is not None:
                gb_right_pos = wx.GBPosition(row, column + 1)
                container_sizer.Add(right_column_sizer, gb_right_pos, flag=wx.ALIGN_CENTER_VERTICAL, border=5)

        return container_sizer

    def __repr__(self):
        return self._type_info.name
