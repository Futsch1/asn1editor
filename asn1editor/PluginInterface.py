import enum
import typing

import asn1tools


class PluginInterface:  # pragma: no cover

    class MessageType(enum.Enum):
        INFO = 1
        WARNING = 2
        ERROR = 3
        QUESTION = 4

    def load_spec(self, file_name: str, type_name: typing.Optional[str] = None):
        """
        Loads an ASN.1 specification in the editor.

        :param file_name: File name of the ASN.1 specification
        :param type_name: Optional type name indication. Format: [Module name].[Type name]
        """
        raise NotImplementedError

    def show_data(self, data: bytes, codec: str):
        """
        Decodes and shows data from an ASN.1 encoded byte stream in the editor.

        :param data: Byte stream with ASN.1 encoded data
        :param codec: Codec to use for decoding (reference asn1tools which ones are supported)
        """
        raise NotImplementedError

    def encode_data(self, codec: str) -> bytes:
        """
        Encodes the data currently edited in the editor window with an ASN.1 codec.

        :param codec: Codec to use for encoding (reference asn1tools which ones are supported)

        :return: Encoded data
        """
        raise NotImplementedError

    def get_spec_filename(self) -> typing.Optional[str]:
        """
        :return: The file name of the ASN.1 specification file currently loaded.
        """
        raise NotImplementedError

    def get_spec(self, codec: str) -> asn1tools.compiler.Specification:
        """
        :param codec: Codec to use (reference asn1tools which ones are supported)

        :return: The compiled ASN.1 specification as an object defined by asn1tools.
        """
        raise NotImplementedError

    def get_typename(self) -> typing.Optional[str]:
        """
        :return: The name of the currently used type name in the editor.
        """
        raise NotImplementedError

    def file_picker(self, message: str, wildcard: str, open_: bool) -> typing.Optional[str]:
        """
        Opens a file picker where the user can choose a file name and returns this chosen name.

        :param message: Message to show in the file picker
        :param wildcard: Wildcards to offer the user in order to help him choose the correct file types
        :param open_: Flag if the dialog shall be an open dialog (True) or a save dialog (false)

        :return: Selected file, None if cancelled
        """
        raise NotImplementedError

    def dir_picker(self, message: str) -> typing.Optional[str]:
        """
        Opens a dir picker where the user can choose a directory name and returns this chosen name.

        :param message: Message to show in the dir picker

        :return: Selected directory, None if cancelled
        """
        raise NotImplementedError

    def text_entry(self, message: str, default: typing.Optional[str] = None) -> typing.Optional[str]:
        """
        Queries a text from the user.

        :param message: Message to show to the user
        :param default: Default value for the text entry

        :return: Entered text, None if cancelled
        """
        raise NotImplementedError

    def choice_entry(self, message: str, caption: str, choices: typing.List[str], default: typing.Optional[str] = None) -> typing.Optional[str]:
        """
        Queries the user for a choice of values.

        :param message: Message to show to the user
        :param caption: Message box caption
        :param choices: List of strings for the user to choose from
        :param default: Default selection

        :return: Selected string, None if cancelled
        """
        raise NotImplementedError

    def show_message(self, message: str, caption: str, message_type: MessageType) -> bool:
        """
        Shows a status message.

        :param message: Message to show to the user
        :param caption: Message box caption
        :param message_type: Type of message box

        :return: If type is a question, True means yes and False means No
        """
        raise NotImplementedError

    def show_status(self, message: str):
        """
        Shows a status message.

        :param message: Message to show to the user
        """
        raise NotImplementedError

    def get_settings(self) -> dict:
        """
        Get a settings dictionary for a plugin to store persistent data

        :return: Settings dict
        """
        raise NotImplementedError

    def show_progress(self, message: str, caption: str, max_progress: typing.Optional[int] = None):
        """
        Shows a progress window

        :param message: Message to show to the user
        :param caption: Message box caption
        :param max_progress: Maximum progress value
        """
        raise NotImplementedError

    def update_progress(self, message: typing.Optional[str] = None, close: bool = False, progress: typing.Optional[int] = None) -> bool:
        """
        Updates a shown progress window

        :param message: Updated message to show to the user, optional
        :param close: If set, window is closed, optional
        :param progress: Progress to show, if none, an indeterminate process is shown, optional

        :return: False if progress window has been canceled, otherwise True
        """
        raise NotImplementedError
