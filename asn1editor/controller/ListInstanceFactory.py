from typing import Dict

from asn1tools.codecs import oer, constraints_checker

from asn1editor.controller.Controller import Controller
from asn1editor.view.AbstractView import ListView, AbstractView
from asn1editor.view.AbstractViewFactory import AbstractViewFactory


class ListInstanceFactory:
    def __init__(self, view_factory: AbstractViewFactory, list_view: ListView, _type: oer.Type, checker: constraints_checker.Type):
        self._view_factory = view_factory
        self._list_view = list_view
        self._type = _type
        self._checker = checker

        self.content_views: Dict[int, AbstractView] = {}

    def create(self, instance: int, parent: Controller):
        from asn1editor.ViewControllerFactory import ViewControllerFactory

        view_factory = ViewControllerFactory(self._view_factory)
        self._type.name = f'Element {instance}'
        self.content_views[instance] = view_factory.create_view_and_controller(self._type, self._checker, parent)

        self._list_view.add(self.content_views[instance])

    def destroy(self, instance: int):
        self._list_view.remove(self.content_views[instance])

        del self.content_views[instance]
