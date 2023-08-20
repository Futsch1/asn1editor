import filecmp
import os
from unittest import TestCase

from asn1editor.ASN1SpecHandler import ASN1SpecHandler
from asn1editor.view.AbstractViewFactory import AbstractViewFactory


class TestASN1SpecHandler(TestCase):
    def test_init_and_get_filenames(self):
        asn1_spec_handler = ASN1SpecHandler(['example/example.asn'])
        self.assertIn('example.asn', asn1_spec_handler.get_filenames()[0])

        asn1_spec_handler = ASN1SpecHandler('tests/standards/rfc1157.asn')
        self.assertIn('rfc1155.asn', [os.path.split(p)[1] for p in asn1_spec_handler.get_filenames()])
        self.assertIn('rfc1157.asn', [os.path.split(p)[1] for p in asn1_spec_handler.get_filenames()])

    def test_invalid_type(self):
        asn1_spec_handler = ASN1SpecHandler(['example/example.asn'])
        with self.assertRaises(Exception):
            asn1_spec_handler.create_view_controller_for_type('Unknown', AbstractViewFactory(), None)

    def test_get_extension(self):
        extension = ASN1SpecHandler.get_extensions()
        self.assertIn('*.jer', extension)
        self.assertIn('*.xer', extension)
        self.assertIn('*.oer', extension)

    def test_load_data_file(self):
        asn1_spec_handler = ASN1SpecHandler(['example/example.asn'])
        with self.assertRaises(AssertionError):
            asn1_spec_handler.load_data_file('example/example.json')

        asn1_spec_handler._type_name = 'Sequence'

        d = asn1_spec_handler.load_data_file('example/example.json')
        self.assertIn('Sequence', d)
        self.assertIn('example1', d['Sequence'])
        self.assertIn('enumerated', d['Sequence'])

        with self.assertRaises(FileNotFoundError):
            asn1_spec_handler.load_data_file('Does_not_exist')

        with self.assertRaises(Exception):
            asn1_spec_handler.load_data_file('example/example.style')

    def test_save_data_file(self):
        asn1_spec_handler = ASN1SpecHandler(['example/example.asn'])
        with self.assertRaises(AssertionError):
            asn1_spec_handler.save_data_file('test.jer', {})

        asn1_spec_handler._type_name = 'Sequence'

        d = asn1_spec_handler.load_data_file('example/example_with_additionals.json')
        asn1_spec_handler.save_data_file('test.jer', d)
        self.assertTrue(filecmp.cmp('test.jer', 'example/example_with_additionals.json', False))

        asn1_spec_handler.save_data_file('test.xml', d)
        d2 = asn1_spec_handler.load_data_file('test.xml')
        self.assertDictEqual(d, d2)

        with self.assertRaises(Exception):
            asn1_spec_handler.save_data_file('test.something', d)
