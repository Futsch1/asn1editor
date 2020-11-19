import wx

from asn1editor.wxPython.WxPythonViews import WxPythonView, WxPythonContainerView


class TreeView:

    @staticmethod
    def __build(tree_ctrl: wx.TreeCtrl, tree_item: wx.TreeItemId, view: WxPythonView):
        if isinstance(view, WxPythonContainerView):
            container_item = tree_ctrl.AppendItem(tree_item, view.get_name())
            for child in view.get_children():
                TreeView.__build(tree_ctrl, container_item, child)
        else:
            tree_ctrl.AppendItem(tree_item, view.get_name())

    @staticmethod
    def get_ctrl(window: wx.Window, root_view: WxPythonView, root_name: str) -> wx.TreeCtrl:
        tree_ctrl = wx.TreeCtrl(window)
        root_id = tree_ctrl.AddRoot(root_name)
        TreeView.__build(tree_ctrl, root_id, root_view)

        return tree_ctrl
