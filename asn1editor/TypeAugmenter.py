import typing

from asn1editor.view.AbstractViewFactory import Styles


class TypeAugmenter:  # pragma: no cover
    def get_style(self, path: str) -> Styles:
        raise NotImplementedError

    def get_help(self, path: str) -> typing.Optional[str]:
        raise NotImplementedError

    def set_spec_filename(self, spec_filename: str):
        raise NotImplementedError
