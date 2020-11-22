import wx

from asn1editor.wxPython.WxPythonComplexViews import WxPythonContainerView
from asn1editor.wxPython.WxPythonViews import WxPythonView


class TreeView:

    def __init__(self, window: wx.Window, content_window: wx.ScrolledWindow):
        self.__views = {}
        self.__window = window
        self.__content_window = content_window

    def __build(self, tree_ctrl: wx.TreeCtrl, tree_item: wx.TreeItemId, view: WxPythonView):
        if isinstance(view, WxPythonContainerView):
            container_item = tree_ctrl.AppendItem(tree_item, view.get_name())
            self.__views[container_item] = view
            for child in view.get_children():
                self.__build(tree_ctrl, container_item, child)

    def get_ctrl(self, root_view: WxPythonView, root_name: str) -> wx.TreeCtrl:
        tree_ctrl = wx.TreeCtrl(self.__window)
        root_id = tree_ctrl.AddRoot(root_name)
        self.__build(tree_ctrl, root_id, root_view)

        tree_ctrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.item_selected)

        return tree_ctrl

    def item_selected(self, e: wx.TreeEvent):
        view = self.__views.get(e.GetItem())
        if view is not None:
            sizer: wx.Sizer = self.__content_window.GetSizer()

            sizer.Add(view.realize().get_sizer(recursive=False), 0, wx.ALL | wx.EXPAND, 5)

            sizer.Layout()

            self.__content_window.SetSizer(sizer)
            self.__content_window.FitInside()
            self.__content_window.AdjustScrollbars()
