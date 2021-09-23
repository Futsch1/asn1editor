import json
import os
import typing

from asn1editor import TypeAugmenter
from asn1editor.view.AbstractViewFactory import Styles


class TestAugmenter(TypeAugmenter):
    def __init__(self, help_text: typing.Optional[str]):
        self.__styles = {}
        self.__help_text = help_text

    def set_spec_filename(self, spec_filename: str):
        style_filename = os.path.splitext(spec_filename)[0] + '.style'
        if os.path.exists(style_filename):
            with open(style_filename) as f:
                self.__styles = json.load(f)

    def get_help(self, path: str) -> typing.Optional[str]:
        return self.__help_text

    def get_style(self, path: str) -> Styles:
        last_path_part = path.split('.')[-1]
        style = Styles(0)
        style_str = self.__styles.get(last_path_part)
        print(path)
        if style_str:
            style = {'read_only': Styles.READ_ONLY, 'hidden': Styles.HIDDEN}[style_str]
        return style
