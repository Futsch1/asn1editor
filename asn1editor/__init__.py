__version__ = "0.4.0"
# noinspection SpellCheckingInspection
__author__ = "Florian Fetz"

from . import wxPython
from .Plugin import Plugin
from .PluginInterface import PluginInterface

__all__ = ['wxPython', 'Plugin', 'PluginInterface']
