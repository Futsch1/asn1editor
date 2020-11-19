from typing import Tuple

import wx

from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.view.AbstractView import ContainerView
from asn1editor.wxPython.Styler import Styler
from asn1editor.wxPython.WxPythonViewFactory import WxPythonViewFactory
from asn1editor.wxPython.treeView.WxPythonTreeViews import WxPythonTreeContainerView


class WxPythonTreeViewFactory(WxPythonViewFactory):

    def __init__(self, window: wx.ScrolledWindow, styler: Styler, name: str):
        super(WxPythonViewFactory, self).__init__(window, styler)
        self.__tree_ctrl = wx.TreeCtrl(window)
        self.__item_id = self.__tree_ctrl.AddRoot(name)

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

        view = WxPythonTreeContainerView(self.__tree_ctrl, self.__item_id, sizer, container_sizer, optional_control)

        return view, view if optional else None
