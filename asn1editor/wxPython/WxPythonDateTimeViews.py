import datetime
import typing

import wx

from asn1editor.interfaces.ValueInterface import ValueInterface
from asn1editor.view.AbstractViewFactory import TypeInfo, Styles
from asn1editor.wxPython.WxPythonViews import WxPythonValueView, ControlList, WxPythonView


class WxPythonDateView(WxPythonValueView):
    def __init__(self, type_info: TypeInfo, controls: ControlList):
        super(WxPythonDateView, self).__init__(type_info, controls)

    def get_value(self) -> datetime.date:
        dt: wx.DateTime = self._controls['value'].GetValue()
        return datetime.date(year=dt.GetYear(), month=dt.GetMonth(), day=dt.GetDay())

    def set_value(self, val: datetime.date):
        self._controls['value'].SetValue(wx.DateTime(day=val.day, month=val.month, year=val.year))


class WxPythonTimeView(WxPythonValueView):
    def __init__(self, type_info: TypeInfo, controls: ControlList):
        super(WxPythonTimeView, self).__init__(type_info, controls)

    def get_value(self) -> datetime.time:
        hour, minute, second = self._controls['value'].GetTime()
        return datetime.time(hour=hour, minute=minute, second=second)

    def set_value(self, val: datetime.time):
        self._controls['value'].SetTime(val.hour, val.minute, val.second)


class WxPythonDateTimeView(WxPythonView, ValueInterface):
    def __init__(self, type_info: TypeInfo, controls: ControlList):
        super(WxPythonDateTimeView, self).__init__(type_info, controls)

    def get_sizer(self, recursive: bool) -> wx.Sizer:
        sizer = self._create_sizer()
        sizer.Add(self._controls['value'], proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        sizer.Add(self._controls['time'], proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        if self._controls.get('style') & Styles.HIDDEN:
            sizer.ShowItems(False)
        return sizer

    def register_change_event(self, callback: typing.Callable):
        # noinspection PyUnusedLocal
        def event_closure(e: wx.Event):
            del e
            callback()

        self._controls['value'].Bind(wx.EVT_TEXT, event_closure)
        self._controls['time'].Bind(wx.EVT_TEXT, event_closure)

    def get_value(self) -> datetime.datetime:
        dt: wx.DateTime = self._controls['value'].GetValue()
        hour, minute, second = self._controls['time'].GetTime()
        return datetime.datetime(year=dt.GetYear(), month=dt.GetMonth(), day=dt.GetDay(),
                                 hour=hour, minute=minute, second=second)

    def set_value(self, val: datetime.datetime):
        self._controls['value'].SetValue(wx.DateTime(day=val.day, month=val.month, year=val.year))
        self._controls['time'].SetTime(val.hour, val.minute, val.second)
