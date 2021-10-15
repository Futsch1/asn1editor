import glob
import json
import locale
import os
import re
import typing
import xml.dom.minidom
from typing import List, Tuple, Dict, Union

import asn1tools

from asn1editor.TypeAugmenter import TypeAugmenter
from asn1editor.ViewControllerFactory import ViewControllerFactory
from asn1editor.controller.Controller import Controller
from asn1editor.view.AbstractView import AbstractView
from asn1editor.view.AbstractViewFactory import AbstractViewFactory


class ASN1SpecHandler:
    IMPORTS_REGEX_OUTER = re.compile(r'IMPORTS([\s\S]*);', flags=re.MULTILINE)
    IMPORTS_REGEX_INNER = re.compile(r'FROM\s*(\S*)', flags=re.MULTILINE)

    def __init__(self, file_name: Union[str, List[str]]):
        # This is necessary to enable parsing of stored dates
        try:
            locale.setlocale(locale.LC_TIME, 'C')
        except locale.Error:
            pass

        if isinstance(file_name, str):
            import_names = []
            # Pre process for import statements to automatically resolve other files
            my_path = os.path.split(os.path.abspath(file_name))[0]
            with open(file_name, 'r', encoding='utf-8') as f:
                content = f.read()
                imports = self.__get_imports(content)
                for imported_type in imports:
                    import_names.extend(self.__search_files_for_imported_type(my_path, imported_type))
                self.__file_names = [os.path.abspath(file_name)] + import_names
        else:
            self.__file_names = [os.path.abspath(f) for f in file_name]
        self.__compiled = {}
        self._type_name = None

    def __get_imports(self, content: str) -> typing.List[str]:
        match = re.search(self.IMPORTS_REGEX_OUTER, content)
        if match is not None:
            inner = match.group(1)
            return [i.group(1).lower() for i in re.finditer(self.IMPORTS_REGEX_INNER, inner)]
        else:
            return []

    @staticmethod
    def __search_files_for_imported_type(search_path: str, imported_type: str) -> typing.List[str]:
        import_names = []
        dir_files = glob.glob(os.path.join(search_path, '*.asn'))
        for dir_file in dir_files:
            dir_file_name = os.path.splitext(os.path.basename(dir_file))[0].lower()
            if imported_type in dir_file_name or dir_file_name in imported_type:
                import_names.append(dir_file)
        return import_names

    def get_filenames(self) -> List[str]:
        return self.__file_names

    def is_loaded(self, file_name: str):
        return os.path.abspath(file_name) in self.__file_names

    def get_types(self, ) -> List[str]:
        types = []
        compiled = self.get_compiled('oer')
        # TODO: Only include those types that are in the originally loaded file
        for module_name, module in compiled.modules.items():
            for type_name, compiled_type in module.items():
                types.append(module_name + '.' + type_name)
        return sorted(types)

    def get_compiled(self, codec: str) -> asn1tools.compiler.Specification:
        if codec not in self.__compiled:
            self.__compiled[codec] = asn1tools.compile_files(self.__file_names, codec)
        return self.__compiled[codec]

    def create_mvc_for_type(self, load_type: str, view_factory: AbstractViewFactory,
                            type_augmenter: typing.Optional[TypeAugmenter]) -> Tuple[AbstractView, Controller]:
        compiled = self.get_compiled('oer')
        for module_name, module in compiled.modules.items():
            for type_name, compiled_type in module.items():

                if module_name + '.' + type_name == load_type:
                    mvc_factory = ViewControllerFactory(view_factory, type_augmenter)
                    self._type_name = type_name
                    return mvc_factory.create(compiled_type)

        raise Exception(f'Requested type {load_type} not found in ASN.1 spec')

    @staticmethod
    def get_extensions() -> List[str]:
        return ['*.json', '*.jer', '*.oer', '*.xml', '*.xer', '*.der', '*.ber', '*.per', '*.uper']

    @staticmethod
    def __get_codec(file_name: str) -> str:
        extension_to_codec = {'.json': 'jer', '.jer': 'jer', '.oer': 'oer', '.xer': 'xer', '.xml': 'xer', '.der': 'der', '.ber': 'ber', '.per': 'per',
                              '.uper': 'uper'}
        extension = os.path.splitext(file_name)[1]
        if extension not in extension_to_codec:
            raise Exception(f'Unknown extension {extension}: No ASN.1 codec found')
        return extension_to_codec[extension]

    def load_data_file(self, file_name: str) -> Dict:
        assert self._type_name is not None

        with open(file_name, 'rb') as f:
            return self.get_model_from_data(f.read(), self.__get_codec(file_name))

    def save_data_file(self, file_name: str, model: Dict):
        assert self._type_name is not None

        codec = self.__get_codec(file_name)
        data = self.get_data_from_model(model, codec)
        # Pretty printing of JSON or XML files
        if codec == 'jer':
            data = json.dumps(json.loads(data), indent=4).encode()
        if codec == 'xer':
            dom = xml.dom.minidom.parseString(data)
            data = dom.toprettyxml().encode()
        with open(file_name, 'wb') as f:
            f.write(data)

    def get_data_from_model(self, model: Dict, codec: str) -> bytes:
        compiled = self.get_compiled(codec)
        return compiled.encode(self._type_name, model[self._type_name], check_constraints=True)

    def get_model_from_data(self, data: bytes, codec: str) -> Dict:
        compiled = self.get_compiled(codec)
        return {self._type_name: compiled.decode(self._type_name, data)}
