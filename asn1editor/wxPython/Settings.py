import json


class Settings:
    def __init__(self):
        try:
            with open('settings.json', 'r') as f:
                self.s = json.load(f)
        except FileNotFoundError:
            self.s = {}
        except json.decoder.JSONDecodeError:
            self.s = {}

    def save(self):
        with open('settings.json', 'w+') as f:
            f.write(json.dumps(self.s))
