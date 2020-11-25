import typing

import wx

from asn1editor.wxPython import Resources
from asn1editor.wxPython.WxPythonComplexViews import WxPythonContainerView, WxPythonChoiceView
from asn1editor.wxPython.WxPythonViews import WxPythonView


class TreeView:

    def __init__(self, window: wx.Window, content_window: wx.ScrolledWindow, root_name: str):
        self.__tree_ctrl = wx.TreeCtrl(window)
        Resources.get_bitmap_from_svg('root')
        root_item = self.__tree_ctrl.AddRoot(root_name, Resources.image_list.get_index('root'))
        self.__tree_ctrl.SetItemBold(root_item, True)
        self.__tree_ctrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.item_selected)
        self.__tree_ctrl.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.item_right_clicked)
        self.__tree_ctrl.SetImageList(Resources.image_list.get_image_list())
        self.__content_window = content_window
        self.__current_view: typing.Optional[WxPythonView] = None

    def __sync(self, tree_item: wx.TreeItemId, view: WxPythonView):
        if isinstance(view, WxPythonContainerView):
            # First, check if the view is not in the tree yet
            container_item_for_view = self.__add_if_not_in_tree(tree_item, view)

            # Now check if it was removed from the tree
            self.__delete_if_removed(container_item_for_view, view.get_children())

            # Finally handle children
            if view.get_has_value():
                for child in view.get_children():
                    self.__sync(container_item_for_view, child)
        if isinstance(view, WxPythonChoiceView):
            container_item_for_view = self.__add_if_not_in_tree(tree_item, view)

            self.__delete_if_removed(container_item_for_view, [view.get_view()])
            if view.get_has_value():
                self.__sync(container_item_for_view, view.get_view())

    def __add_if_not_in_tree(self, tree_item: wx.TreeItemId, view: typing.Union[WxPythonContainerView, WxPythonChoiceView]) -> typing.Optional[wx.TreeItemId]:
        # First, check if the view is not in the tree yet
        found = False
        container_item_for_view = None
        tree_child, cookie = self.__tree_ctrl.GetFirstChild(tree_item)
        while tree_child.IsOk():
            child_view = self.__tree_ctrl.GetItemData(tree_child)
            if child_view == view:
                container_item_for_view = tree_child
                found = True
            tree_child, cookie = self.__tree_ctrl.GetNextChild(tree_child, cookie)
        if not found:
            image = Resources.image_list.get_index(view.icon)
            container_item_for_view = self.__tree_ctrl.AppendItem(tree_item, view.get_name(), image=image)
            self.__tree_ctrl.SetItemData(container_item_for_view, view)

        self.__tree_ctrl.SetItemBold(container_item_for_view, view.get_has_value())

        return container_item_for_view

    def __delete_if_removed(self, container_item_for_view: wx.TreeItemId, views: typing.List[WxPythonView]):
        current_child_views_in_tree = []
        tree_child, cookie = self.__tree_ctrl.GetFirstChild(container_item_for_view)
        while tree_child.IsOk():
            current_child_views_in_tree.append((self.__tree_ctrl.GetItemData(tree_child), tree_child))
            tree_child, cookie = self.__tree_ctrl.GetNextChild(tree_child, cookie)

        for current_child, current_treeitem in current_child_views_in_tree:
            if current_child not in views:
                self.__tree_ctrl.Delete(current_treeitem)

    def get_ctrl(self, root_view: WxPythonView) -> wx.TreeCtrl:
        self.__sync(self.__tree_ctrl.GetRootItem(), root_view)
        root_view.set_visible(False, recursive=True)

        selected = self.__tree_ctrl.GetSelection()
        if selected.IsOk() and self.__tree_ctrl.GetItemData(selected) is not None:
            self.__show_view(self.__tree_ctrl.GetItemData(selected))

        self.__tree_ctrl.Show()
        return self.__tree_ctrl

    def hide(self):
        self.__current_view = None
        self.__tree_ctrl.Hide()

    def destroy(self):
        self.__tree_ctrl.Destroy()

    def item_selected(self, e: wx.TreeEvent):
        view = self.__tree_ctrl.GetItemData(e.GetItem())
        if view is not None:
            self.__show_view(view)

    def item_right_clicked(self, e: wx.TreeEvent):
        class RightClickMenu(wx.Menu):
            def __init__(self, parent):
                super(RightClickMenu, self).__init__()
                self.parent = parent

                self.expand = self.Append(wx.NewId(), 'Expand')
                self.expand_all = self.Append(wx.NewId(), 'Expand all')
                self.AppendSeparator()
                self.collapse = self.Append(wx.NewId(), 'Collapse')
                self.collapse_all = self.Append(wx.NewId(), 'Collapse all')

        menu = RightClickMenu(self.__tree_ctrl.GetTopLevelParent())
        menu.Bind(wx.EVT_MENU, lambda _: self.__tree_ctrl.ExpandAllChildren(e.GetItem()), menu.expand)
        menu.Bind(wx.EVT_MENU, lambda _: self.__tree_ctrl.ExpandAll(), menu.expand_all)
        menu.Bind(wx.EVT_MENU, lambda _: self.__tree_ctrl.CollapseAllChildren(e.GetItem()), menu.collapse)
        menu.Bind(wx.EVT_MENU, lambda _: self.__tree_ctrl.CollapseAll(), menu.collapse_all)
        self.__tree_ctrl.GetTopLevelParent().PopupMenu(menu, e.GetPoint())

    def __show_view(self, view: WxPythonView):
        self.__content_window.GetTopLevelParent().Freeze()

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

        self.__content_window.GetTopLevelParent().Thaw()
