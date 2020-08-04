[![Build Status](https://travis-ci.org/Futsch1/asn1editor.svg?branch=master)](https://travis-ci.org/Futsch1/asn1editor)
[![Coverage Status](https://coveralls.io/repos/github/Futsch1/asn1editor/badge.svg?branch=master)](https://coveralls.io/github/Futsch1/asn1editor?branch=master)
# asn1editor
Python based ASN.1 editor

This project contains a generic editor to view ASN.1 encoded data. 
It can load and save data encoded in various ASN.1 formats. 

The controller part of the editor is written independently from the 
used GUI framework. A view implementation with wxPython is provided and
can be started by running wxEditor.

## Plugin interface

In order to use custom data formats or to work with the data, plugins
can be used. These plugins need to inherit from the Plugin.Plugin class and
can use the PluginInterface.PluginInterface class to interact with the
main application. 