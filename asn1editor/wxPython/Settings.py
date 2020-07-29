import json

settings = {}


def load():
    global settings
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {}
    except json.decoder.JSONDecodeError:
        settings = {}


def save():
    global settings
    with open('settings.json', 'w+') as f:
        f.write(json.dumps(settings))
