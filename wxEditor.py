import argparse

import wx

from asn1editor.wxPython.MainWindow import MainWindow

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ASN.1 editor')
    parser.add_argument('-asn1spec', required=False, help='ASN.1 specification file name')
    parser.add_argument('-type', required=False, help='Name of the ASN.1 type to load (Module name.Type name)')
    parser.add_argument('-data', required=False, help='Data file to load')

    args = parser.parse_args()

    app = wx.App()

    frame = MainWindow()
    if args.asn1spec is not None:
        frame.load_spec(args.asn1spec, args.type)
        app.ProcessPendingEvents()
    if args.data is not None:
        frame.load_data_from_file(args.data)

    frame.Show()

    app.MainLoop()
