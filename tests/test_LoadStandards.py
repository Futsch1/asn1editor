import glob
from unittest import TestCase

import asn1editor
from asn1editor.ASN1SpecHandler import ASN1SpecHandler
from tests import testHelper


class LoadStandardsTest(TestCase):
    def __load_standards(self, main_window):
        tested_types = set()
        for file in glob.glob('tests/standards/*'):
            print(f'Loading types from {file}')
            asn1_handler = ASN1SpecHandler(file)
            types = asn1_handler.get_types()
            for type_ in types:
                if type_ in tested_types:
                    continue
                print(f'  Loading {type_}')
                main_window.load_spec(file, type_)
                self.assertEqual(main_window.get_spec_filename(), file)
                self.assertEqual(main_window.get_typename(), type_)
                tested_types.add(type_)

    def test_load_standards(self):
        # noinspection PyUnusedLocal
        app = testHelper.get_wx_app()
        main_window = asn1editor.wxPython.MainWindow()
        self.__load_standards(main_window)
