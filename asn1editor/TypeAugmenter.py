import typing

from asn1editor.view.AbstractViewFactory import Styles


class TypeAugmenter:  # pragma: no cover
    """
    Class to be implemented to provide additional styling info and help texts for ASN.1 elements.

    Intention is to have a database/parallel file to the ASN.1 specification that provides user configurable meta information
    """

    def get_style(self, path: str) -> Styles:
        """
        @param path: Path of the element
        @return: Style flags for the element
        """
        raise NotImplementedError

    def get_help(self, path: str) -> typing.Optional[str]:
        """
        @param path: Path of the element
        @return: Optional help text
        """
        raise NotImplementedError

    def set_spec_filename(self, spec_filename: str):
        """
        Set when a new spec was loaded to indicate which ASN.1 specification further requests are based on.
        @param spec_filename: File name of loaded spec
        """
        raise NotImplementedError
