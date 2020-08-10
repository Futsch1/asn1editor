import json
import os
import sys

settings = {}


def _get_filename():
    if sys.platform == 'win32':
        win_path = os.path.expandvars(r'%APPDATA%/asn1editor')
        os.makedirs(win_path, exist_ok=True)
        return os.path.join(win_path, 'settings.json')
    elif sys.platform.startswith('linux'):
        home = os.path.expanduser('~/.local/share/asn1editor')
        os.makedirs(home, exist_ok=True)
        return os.path.join(home, 'settings.json')
    else:
        return 'settings.json'


def load():
    global settings
    try:
        with open(_get_filename(), 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {}
    except json.decoder.JSONDecodeError:
        settings = {}


def save():
    global settings
    with open(_get_filename(), 'w+') as f:
        f.write(json.dumps(settings))
