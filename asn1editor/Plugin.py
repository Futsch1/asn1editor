import typing

from asn1editor import PluginInterface


class Plugin:  # pragma: no cover
    def get_name(self) -> str:
        """
        Returns the name of a plugin - used to name the menu item folder
        """
        raise NotImplementedError

    def get_menus(self) -> typing.List[typing.Tuple[str, typing.Callable]]:
        """
        Get the menus required by the plugin.

        Returns a list of strings and callables, where the string is the menu caption and
        the callable a callback that will be executed when the menu item is selected.
        """
        raise NotImplementedError

    def get_tools(self) -> typing.List[typing.Tuple[str, str, str, typing.Callable]]:
        """
        Get the toolbar items required by the plugin.

        Returns a list of strings and callables, where the strings are the label, the tool tip
        and a path to an icon, the callable a callback that will be executed when the menu
        item is selected.
        """
        raise NotImplementedError

    def connect(self, plugin_interface: PluginInterface):
        """
        Connects the plugin host and the plugin.

        The function will be called during startup and serves to register the PluginInterface.

        :param plugin_interface: Object that implements the PluginInterface.
        """
        raise NotImplementedError
