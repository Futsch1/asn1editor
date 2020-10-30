import json
import os
import typing


class Styler:
    def __init__(self, style_file_name: str):
        self.__styles = {}
        if os.path.exists(style_file_name):
            with open(style_file_name) as f:
                self.__styles = json.load(f)

    def get_style(self, name: str) -> typing.Optional[str]:
        return self.__styles.get(name)
