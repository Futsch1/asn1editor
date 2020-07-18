import typing

from asn1editor import PluginInterface


class Plugin:
    def get_name(self) -> str:
        raise NotImplementedError

    def get_menus(self) -> typing.List[typing.Tuple[str, typing.Callable]]:
        raise NotImplementedError

    def connect(self, plugin_interface: PluginInterface):
        raise NotImplementedError
