__version__ = "0.7.2"
# noinspection SpellCheckingInspection
__author__ = "Florian Fetz"

import argparse

import wx

from .Plugin import Plugin
from .PluginInterface import PluginInterface
from .TypeAugmenter import TypeAugmenter
from .wxPython import MainWindow as WxPythonMainWindow

__all__ = ['WxPythonMainWindow', 'Plugin', 'PluginInterface', 'TypeAugmenter']


def _wx_python_editor():
    parser = argparse.ArgumentParser(description='ASN.1 editor')
    parser.add_argument('asn1spec', nargs='?', help='ASN.1 specification file name')
    parser.add_argument('-type', required=False, help='Name of the ASN.1 type to load (Module name.Type name)')
    parser.add_argument('-data', required=False, help='Data file to load')

    args = parser.parse_args()

    app = wx.App()

    frame = WxPythonMainWindow()
    if args.asn1spec is not None:
        frame.load_spec(args.asn1spec, args.type)
    if args.data is not None:
        frame.load_data_from_file(args.data)

    frame.Show()

    app.MainLoop()
