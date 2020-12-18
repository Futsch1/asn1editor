import datetime

import wx

from asn1editor.wxPython.WxPythonViews import WxPythonValueView, ControlList


class WxPythonDateView(WxPythonValueView):
    def __init__(self, name: str, controls: ControlList):
        super(WxPythonDateView, self).__init__(name, controls)

    def get_value(self) -> datetime.date:
        dt: wx.DateTime = self._controls['value'].GetValue()
        return datetime.date(year=dt.GetYear(), month=dt.GetMonth(), day=dt.GetDay())

    def set_value(self, val: datetime.date):
        dt = wx.DateTime(day=val.day, month=val.month, year=val.year)
        self._controls['value'].SetValue(dt)


class WxPythonTimeView(WxPythonValueView):
    def __init__(self, name: str, controls: ControlList):
        super(WxPythonTimeView, self).__init__(name, controls)

    def get_value(self) -> datetime.time:
        hour, minute, second = self._controls['value'].GetTime()
        return datetime.time(hour=hour, minute=minute, second=second)

    def set_value(self, val: datetime.time):
        self._controls['value'].SetTime(val.hour, val.minute, val.second)
