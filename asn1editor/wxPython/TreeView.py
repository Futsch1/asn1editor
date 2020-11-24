import typing

import wx

from asn1editor.wxPython.WxPythonComplexViews import WxPythonContainerView, WxPythonChoiceView
from asn1editor.wxPython.WxPythonViews import WxPythonView


class TreeView:

    def __init__(self, window: wx.Window, content_window: wx.ScrolledWindow, root_name: str):
        self.__tree_ctrl = wx.TreeCtrl(window)
        self.__tree_ctrl.AddRoot(root_name)
        self.__tree_ctrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.item_selected)
        self.__content_window = content_window
        self.__current_view: typing.Optional[WxPythonView] = None

    def __sync(self, tree_item: wx.TreeItemId, view: WxPythonView):
        if isinstance(view, WxPythonContainerView):
            tree_child, cookie = self.__tree_ctrl.GetFirstChild(tree_item)
            found = False
            container_item = None
            while tree_child.IsOk():
                if self.__tree_ctrl.GetItemData(tree_child) == view:
                    container_item = tree_child
                    found = True
                tree_child, cookie = self.__tree_ctrl.GetNextChild(tree_child, cookie)
            if not found:
                container_item = self.__tree_ctrl.AppendItem(tree_item, view.get_name())
                self.__tree_ctrl.SetItemData(container_item, view)

            # TODO: Check the other way around: view is no longer present

            for child in view.get_children():
                self.__sync(container_item, child)
        if isinstance(view, WxPythonChoiceView):
            pass

    def get_ctrl(self, root_view: WxPythonView) -> wx.TreeCtrl:
        self.__sync(self.__tree_ctrl.GetRootItem(), root_view)
        root_view.set_visible(False, recursive=True)

        selected = self.__tree_ctrl.GetSelection()
        if selected.IsOk():
            self.__show_view(self.__tree_ctrl.GetItemData(selected))

        return self.__tree_ctrl

    def item_selected(self, e: wx.TreeEvent):
        view = self.__tree_ctrl.GetItemData(e.GetItem())
        if view is not None:
            self.__show_view(view)

    def __show_view(self, view: WxPythonView):
        if self.__current_view is not None:
            self.__current_view.set_visible(False, recursive=False)

        self.__current_view = view
        view.set_visible(True, recursive=False)
        sizer: wx.Sizer = self.__content_window.GetSizer()
        sizer.Clear()

        sizer.Add(view.realize().get_sizer(recursive=False), 0, wx.ALL | wx.EXPAND, 5)

        sizer.Layout()

        self.__content_window.SetSizer(sizer)
        self.__content_window.FitInside()
        self.__content_window.AdjustScrollbars()
