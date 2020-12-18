![Build](https://github.com/Futsch1/asn1editor/workflows/Build/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/Futsch1/asn1editor/badge.svg?branch=master)](https://coveralls.io/github/Futsch1/asn1editor?branch=master)
# asn1editor
Python based ASN.1 editor

This project contains a generic editor to view and edit ASN.1 encoded data. 
It can load and save data encoded in various ASN.1 formats. It uses
[asn1tools](https://github.com/eerimoq/asn1tools) to parse
ASN.1 specifications and read and write encoded data.

The controller part of the editor is written independently of the 
used GUI framework. A view implementation with wxPython is provided.

## Features

### Supported types
The editor supports a large variety of ASN.1 data types:
- INTEGER
- REAL
- ENUMERATED
- BOOLEAN
- OCTET STRING, VisibleString, UTF8String, GeneralString, IA5String, OBJECT IDENTIFIER
- BIT STRING
- SEQUENCE, SET
- SEQUENCE OF, SET OF
- CHOICE

The following types are not supported yet:
- DATE, TIME-OF-DAY, DATE-TIME, DURATION
- GeneralizedTime, UTCTime

### Supported encodings
The following encodings are supported for reading and writing data:
- JER
- OER
- XER
- DER
- BER
- PER 
- UPER

### IMPORTS
IMPORT references are automatically resolved if the ASN1 files containing the imported types 
reside in the same directory and have the extension ".asn". 

## Usage
To start the wxPython based editor, install asn1editor via pip:

```pip install asn1editor```

Then you can run asn1editor from the shell

```asn1editor [-h] [-type TYPE] [-data DATA] [asn1spec]```

The ASN.1 specification to be loaded can be passed as an (optional) argument. The type inside the ASN.1 specification can be selected
using the syntax <Namespace>.<Type name>. Finally, a data file can be passed as well that contains data encoded in the ASN.1 specification.

### Extending asn1editor

If you want to extend asn1editor with custom functionality, you can pass a plugin object to the WxPythonMainWindow object.
The plugin object needs to inherit from asn1editor.Plugin.

Example:

```python
import wx
from asn1editor import WxPythonMainWindow, Plugin

class MyPlugin(Plugin):
    # Implementation of abstract functions goes here
    pass

app = wx.App()

frame = WxPythonMainWindow(MyPlugin)

frame.Show()

app.MainLoop()
```

## Plugin interface
In order to use custom data formats or to work with the data, plugins
can be used. These plugins need to inherit from the Plugin.Plugin class and
can use the PluginInterface.PluginInterface class to interact with the
main application. A list of plugins can be passed to the constructor of the main editor class
and is then automatically embedded in the application.

An example application is if a custom header is added to an ASN.1 encoded data. Then the plugin
can decode the header, choose the appropriate ASN.1 specification, load it, decode the data and display it.
