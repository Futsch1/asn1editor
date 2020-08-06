import os


def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource required for PyInstaller """
    # noinspection SpellCheckingInspection
    base_path = os.environ.get("_MEIPASS2", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
