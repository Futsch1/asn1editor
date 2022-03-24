from asn1editor.view.AbstractViewFactory import TypeInfo
from asn1editor.wxPython import ViewSelect


class Labels:
    def __init__(self, view_select: ViewSelect.ViewSelect):
        self.__view_select = view_select

    def get_label(self, type_info: TypeInfo, suffix: str = '') -> str:
        label = ('... ' if type_info.additional else '') + type_info.name + suffix
        if self.__view_select.tag_info == ViewSelect.TagInfo.LABELS and len(type_info.tag):
            label += f' [{type_info.tag}]'

        return label

    def get_tooltip(self, type_info: TypeInfo) -> str:
        tooltip = ['Type: ' + type_info.typename]
        if self.__view_select.tag_info == ViewSelect.TagInfo.TOOLTIPS and len(type_info.tag):
            tooltip += [f'Tag: {type_info.tag}']
        if type_info.optional:
            tooltip += ['Optional element']
        if type_info.additional:
            tooltip += ['Additional element']
        if type_info.help and len(type_info.help):
            tooltip += [f'Help: {type_info.help}']
        return '\n'.join(tooltip)
