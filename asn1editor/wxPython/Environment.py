import json
import os
import sys

settings = {}


def _get_dir() -> str:
    if sys.platform == 'win32':
        win_path = os.path.expandvars(r'%APPDATA%/asn1editor')
        os.makedirs(win_path, exist_ok=True)
        return win_path
    elif sys.platform.startswith('linux'):
        home = os.path.expanduser('~/.local/share/asn1editor')
        os.makedirs(home, exist_ok=True)
        return home
    else:
        return ''


def _get_settings_filename() -> str:
    return os.path.join(_get_dir(), 'settings.json')


def log_error(log_message: str):
    try:
        with open(os.path.join(_get_dir(), 'error_log.txt'), 'a+') as f:
            import datetime
            f.write(f'{datetime.datetime.now()}: {log_message}\n\n')
    finally:
        pass


def load():
    global settings
    try:
        with open(_get_settings_filename(), 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {}
    except json.decoder.JSONDecodeError:
        settings = {}


def save():
    global settings
    with open(_get_settings_filename(), 'w+') as f:
        f.write(json.dumps(settings))
