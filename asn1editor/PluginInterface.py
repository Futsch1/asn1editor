import typing

import asn1tools


class PluginInterface:
    def load_spec(self, file_name: str, type_name: typing.Optional[str] = None):
        raise NotImplementedError

    def show_data(self, data: bytes, codec: str):
        raise NotImplementedError

    def encode_data(self, codec: str) -> bytes:
        raise NotImplementedError

    def get_spec_filename(self) -> str:
        raise NotImplementedError

    def get_spec(self, codec: str) -> asn1tools.compiler.Specification:
        raise NotImplementedError

    def get_typename(self) -> str:
        raise NotImplementedError

    def file_picker(self, message: str, wildcard: str, open_: bool) -> typing.Optional[str]:
        raise NotImplementedError

    def dir_picker(self, message: str) -> typing.Optional[str]:
        raise NotImplementedError
