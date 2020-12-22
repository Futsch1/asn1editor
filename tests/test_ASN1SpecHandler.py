import filecmp
import os
from unittest import TestCase

from asn1editor.ASN1SpecHandler import ASN1SpecHandler
from asn1editor.view.AbstractViewFactory import AbstractViewFactory


class TestASN1SpecHandler(TestCase):
    def test_init_and_get_filenames(self):
        asn1spechandler = ASN1SpecHandler(['example/example.asn'])
        self.assertEqual(['example/example.asn'], asn1spechandler.get_filenames())

        asn1spechandler = ASN1SpecHandler('tests/standards/rfc1157.asn')
        self.assertIn('rfc1155.asn', [os.path.split(p)[1] for p in asn1spechandler.get_filenames()])
        self.assertIn('rfc1157.asn', [os.path.split(p)[1] for p in asn1spechandler.get_filenames()])

    def test_invalid_type(self):
        asn1spechandler = ASN1SpecHandler(['example/example.asn'])
        with self.assertRaises(Exception):
            asn1spechandler.create_mvc_for_type('Unknown', AbstractViewFactory())

    def test_get_extension(self):
        extension = ASN1SpecHandler.get_extensions()
        self.assertIn('*.jer', extension)
        self.assertIn('*.xer', extension)
        self.assertIn('*.oer', extension)

    def test_load_data_file(self):
        asn1spechandler = ASN1SpecHandler(['example/example.asn'])
        with self.assertRaises(AssertionError):
            asn1spechandler.load_data_file('example/example.json')

        asn1spechandler._type_name = 'Sequence'

        d = asn1spechandler.load_data_file('example/example.json')
        self.assertIn('Sequence', d)
        self.assertIn('example1', d['Sequence'])
        self.assertIn('enumerated', d['Sequence'])

        with self.assertRaises(FileNotFoundError):
            asn1spechandler.load_data_file('Does_not_exist')

        with self.assertRaises(Exception):
            asn1spechandler.load_data_file('example/example.style')

    def test_save_data_file(self):
        asn1spechandler = ASN1SpecHandler(['example/example.asn'])
        with self.assertRaises(AssertionError):
            asn1spechandler.save_data_file('test.jer', {})

        asn1spechandler._type_name = 'Sequence'

        d = asn1spechandler.load_data_file('example/example.json')
        asn1spechandler.save_data_file('test.jer', d)
        self.assertTrue(filecmp.cmp('test.jer', 'example/example.json', False))

        asn1spechandler.save_data_file('test.xml', d)
        d2 = asn1spechandler.load_data_file('test.xml')
        self.assertDictEqual(d, d2)

        with self.assertRaises(Exception):
            asn1spechandler.save_data_file('test.something', d)
