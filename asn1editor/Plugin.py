import typing

from asn1editor import PluginInterface


class Plugin:  # pragma: no cover
    """
    Base class for all plugins.

    The methods in this class are used by the UI to display the menus and toolbar items the plugin provides and to perform given callbacks
    when the user interacts with these menu items.

    Additionally, the function connect is called during startup and serves to register the PluginInterface to enable the plugin to access data in
    the loaded ASN.1 specification and to further interact with the user.
    """
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

    def get_about(self) -> typing.Optional[str]:
        """
        Gets an optional about-box string.

        Returns an optional about-box string that will be displayed in the about-box of the plugin.
        """
        raise NotImplementedError

    def connect(self, plugin_interface: PluginInterface):
        """
        Connects the plugin host and the plugin.

        The function will be called during startup and serves to register the PluginInterface.

        @param plugin_interface: Object that implements the PluginInterface.
        """
        raise NotImplementedError
