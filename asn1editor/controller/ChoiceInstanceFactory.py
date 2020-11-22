from typing import Dict, Optional

from asn1tools.codecs import oer, constraints_checker

from asn1editor.controller.Controller import Controller
from asn1editor.view.AbstractView import AbstractView, ChoiceView
from asn1editor.view.AbstractViewFactory import AbstractViewFactory


class ChoiceInstanceFactory:
    def __init__(self, view_factory: AbstractViewFactory, choice_view: ChoiceView, members: Dict[str, oer.Type], checkers: Dict[str, constraints_checker.Type]):
        self._view_factory = view_factory
        self._choice_view = choice_view
        self._members = members
        self._checkers = checkers

        self._content_view: Optional[AbstractView] = None
        self._member = None

    def create(self, member: str, parent: Controller):
        from asn1editor.ViewControllerFactory import ViewControllerFactory

        if member != self._member:
            view_factory = ViewControllerFactory(self._view_factory)

            self._content_view = view_factory.create_view_and_controller(self._members[member], self._checkers[member], parent)
            self._member = member
            self._choice_view.set_view(self._content_view)
