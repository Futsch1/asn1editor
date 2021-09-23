import typing

from asn1editor.view.AbstractViewFactory import Styles


class TypeAugmenter:  # pragma: no cover
    def get_style(self, path: str) -> Styles:
        raise NotImplementedError

    def get_help(self, path: str) -> typing.Optional[str]:
        raise NotImplementedError
