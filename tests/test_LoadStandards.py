import glob
import os
import random
from unittest import TestCase

import asn1editor
from asn1editor.ASN1SpecHandler import ASN1SpecHandler
from asn1editor.wxPython.ViewSelect import ViewType, TagInfo
from tests import TestHelper


class LoadStandardsTest(TestCase):
    def __load_standards(self, main_window):
        tested_types = set()
        for file in glob.glob('tests/standards/*'):
            if os.path.isdir(file):
                continue
            print(f'Loading types from {file}')
            asn1_handler = ASN1SpecHandler(file)
            types = asn1_handler.get_types()
            if os.getenv('ASN1EDITOR_QUICK_TESTS') is not None:
                types = random.sample(types, min(5, len(types)))
            for type_ in types:
                if type_ in tested_types:
                    continue
                print(f'  Loading {type_}')
                self.assertTrue(main_window.load_spec(file, type_))
                self.assertEqual(main_window.get_spec_filename(), file)
                self.assertEqual(main_window.get_typename(), type_)
                tested_types.add(type_)

    def test_load_standards(self):
        # noinspection PyUnusedLocal
        app = TestHelper.get_wx_app()
        main_window = asn1editor.wxPython.MainWindow()
        main_window.select_view_and_tag_info(ViewType.GROUPS, TagInfo.LABELS)
        self.__load_standards(main_window)
