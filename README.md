![Build](https://github.com/Futsch1/asn1editor/workflows/Build/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/Futsch1/asn1editor/badge.svg?branch=master)](https://coveralls.io/github/Futsch1/asn1editor?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/b2492b88948ace2e8a14/maintainability)](https://codeclimate.com/github/Futsch1/asn1editor/maintainability)
# asn1editor
Python based ASN.1 editor

This project contains a generic editor to view and edit ASN.1 encoded data. 
It can load and save data encoded in various ASN.1 formats. It uses
[asn1tools](https://github.com/eerimoq/asn1tools) to parse
ASN.1 specifications and read and write encoded data.

The controller part of the editor is written independently of the 
used GUI framework. A view implementation with wxPython is provided.

![Screenshot](docs/screenshot_tree.png?raw=true "asn1editor")

## Usage
To start the wxPython based editor, install asn1editor via pip:

```pip install asn1editor```

Then you can run asn1editor from the shell

```asn1editor [-h] [-type TYPE] [-data DATA] [asn1spec]```

The ASN.1 specification to be loaded can be passed as an (optional) argument. The type inside the ASN.1 specification can be selected using the syntax < Module
name >.< Type name >. Finally, a data file can be passed as well that contains data encoded in the ASN.1 specification.

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
- DATE, TIME-OF-DAY, DATE-TIME, GeneralizedTime, UTCTime

### Supported encodings
The following encodings are supported for reading and writing data:

- JER
- OER
- XER
- DER
- BER
- PER
- UPER

### GUI features
- Load and save encoded data
- View the data in a tree view or as groups
![Screenshot](docs/screenshot_groups.png?raw=true "asn1editor group view")
- See limits of numeric values and texts as tooltips
- Edit octet strings as ASCII or hex
- List of recently opened specifications for quick access
- Optional dark mode

### IMPORTS
IMPORT references are automatically resolved if the ASN1 files containing the imported types 
reside in the same directory and have the extension ".asn". 

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

frame = WxPythonMainWindow([MyPlugin()])

frame.Show()

app.MainLoop()
```

## Plugin interface

In order to use custom data formats or to work with the data, plugins can be used. These plugins need to inherit from the Plugin.Plugin class and can use the
PluginInterface.PluginInterface class to interact with the main application. A list of plugins can be passed to the constructor of the main editor class and is
then automatically embedded in the application.

An example application is if a custom header is added to an ASN.1 encoded data. Then the plugin can decode the header, choose the appropriate ASN.1
specification, load it, decode the data and display it.

## Type augmenter

The editor can be customized to modify the display of certain fields. This customization is provided via a class that implements the TypeAugmenter interface.
The editor will query additional information for every field via this interface. Currently, a field can be augmented by providing a help text and a style
IntEnum. The help text will be shown in the tooltip of each field and the style flag modifes the way how a field is displayed. A field can be hidden or be
declared as read-only.

The editor comes with a default implementation of this augmenter that uses a .style file to customize the way fields are displayed in asn1editor.

If an ASN.1 file is opened, asn1editor looks for an equally named file with a .style extension in the same directory. If it is found, it is loaded and used to
refine the layout of the specification. A style file is in JSON format and contains the name of the ASN.1 field as a key, and the layout specifier as value. The
specifiers are named "read_only" and "hidden".

Example:

  ```json
  {
  "firstField": "read_only",
  "secondField": "hidden"
}
  ```

## Tests

Apart from unit tests in the source folder, there is a project on testquality.com that contains a number of manual tests to qualify an asn1editor
release [here](https://futsch1.testquality.com). You can log in using the credentials futsch1@fehlbar.de/readonly to view the test cases and test results.
