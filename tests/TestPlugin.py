import time
import typing

from asn1editor import Plugin, PluginInterface


class TestPlugin(Plugin):
    def __init__(self, instance=''):
        self.plugin_interface: typing.Optional[PluginInterface] = None
        self.instance = instance

    def get_name(self) -> str:
        return 'Test' + self.instance

    def get_menus(self) -> typing.List[typing.Tuple[str, typing.Callable]]:
        return [('FileDialog', self.__open_file_dialog),
                ('DirDialog', self.__open_dir_dialog),
                ('TextEntry', self.__open_text_entry),
                ('ChoiceEntry', self.__open_choice_entry),
                ('ProgressDialog', self.__open_progress_dialog),
                ('Question', self.__open_question)]

    def get_tools(self) -> typing.List[typing.Tuple[str, str, str, typing.Callable]]:
        return [('Toolbar', 'Toolbar tooltip', 'tests/test.png', self.__open_tooltip)]

    def connect(self, plugin_interface: PluginInterface):
        self.plugin_interface = plugin_interface

    def __open_file_dialog(self):
        ret = self.plugin_interface.file_picker('Test open file', '*.*', True)
        self.plugin_interface.show_status(str(ret))
        ret = self.plugin_interface.file_picker('Test save file', '*.*', False)
        self.plugin_interface.show_status(str(ret))

    def __open_dir_dialog(self):
        ret = self.plugin_interface.dir_picker('Test')
        self.plugin_interface.show_status(str(ret))

    def __open_text_entry(self):
        ret = self.plugin_interface.text_entry('Test', '123')
        self.plugin_interface.show_status(str(ret))

    def __open_choice_entry(self):
        ret = self.plugin_interface.choice_entry('Test', 'TestC', ['1', '2', '3'], '2')
        self.plugin_interface.show_status(str(ret))

        ret = self.plugin_interface.choice_entry('Test', 'TestC', ['1', '2', '3'], '4')
        self.plugin_interface.show_status(str(ret))

    def __open_progress_dialog(self):
        self.plugin_interface.show_progress('Test', 'TestC', 10)
        for i in range(10):
            time.sleep(0.5)
            running = self.plugin_interface.update_progress(f'Test {i}', progress=i)
            if not running:
                self.plugin_interface.show_status('Closed')

        self.plugin_interface.update_progress('Done', close=True)

        self.plugin_interface.show_progress('Test2', 'TestC')
        for i in range(10):
            time.sleep(0.5)
            running = self.plugin_interface.update_progress(f'Test2 {i}')
            if not running:
                self.plugin_interface.show_status('Closed2')

        self.plugin_interface.update_progress('Done', close=True)

    def __open_question(self):
        self.plugin_interface.show_status(str(self.plugin_interface.show_message('Test?', 'TestC', PluginInterface.MessageType.QUESTION)))

    def __open_tooltip(self):
        self.plugin_interface.show_message('Tooltip', 'Tooltip was clicked', PluginInterface.MessageType.INFO)
