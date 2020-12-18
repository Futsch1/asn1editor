import glob
from unittest import TestCase

import wx

import asn1editor
from asn1editor.ASN1SpecHandler import ASN1SpecHandler


class LoadStandardsTest(TestCase):
    def __load_standards(self, main_window):
        for file in glob.glob('tests/standards/*'):
            asn1_handler = ASN1SpecHandler(file)
            types = asn1_handler.get_types()
            for type_ in types:
                main_window.load_spec(file, type_)
                self.assertEqual(main_window.get_spec_filename(), file)
                self.assertEqual(main_window.get_typename(), type_)

    def test_load_standards(self):
        # noinspection PyUnusedLocal
        app = wx.App()
        main_window = asn1editor.wxPython.MainWindow()

        self.__load_standards(main_window)

        app.Destroy()
