from typing import Optional, Dict

import wx

from asn1editor.view.AbstractView import ContainerView
from asn1editor.wxPython.WxPythonViews import WxPythonView, WxPythonContainerView


class WxPythonTreeContainerView(WxPythonContainerView, ContainerView):
    def __init__(self, tree_ctrl: wx.TreeCtrl, parent: Optional[wx.TreeItemId], sizer: wx.Sizer, container_sizer: wx.FlexGridSizer,
                 optional_control: Optional[wx.CheckBox] = None):
        super(WxPythonContainerView, self).__init__(sizer, optional_control)
        self._container_sizer = container_sizer
        self._children: Dict[str, wx.Sizer] = {}
        self._tree_ctrl = tree_ctrl
        self._parent_tree_id = parent

    def add_child(self, view: WxPythonView, name: str):
        if self.any_shown(view._sizer):
            self._children[name] = view._sizer
            self._container_sizer.Add(view._sizer)
            if not self.get_has_value():
                self._sizer.Hide(view._sizer, recursive=True)

            view.add_parent(self)
            self._tree_ctrl.AppendItem(self._parent_tree_id, name)

    def enable(self, enabled: bool):
        if enabled:
            for child in self._children.values():
                self._sizer.Show(child, recursive=True)
        else:
            for child in self._children.values():
                self._sizer.Hide(child, recursive=True)
        self._sizer.Layout()
        containing_window = self._sizer.GetContainingWindow()
        if containing_window is not None:
            self._sizer.GetContainingWindow().Layout()

    @staticmethod
    def any_shown(sizer: wx.Sizer) -> bool:
        return any([child.IsShown() for child in sizer.GetChildren()])
