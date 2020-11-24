from abc import ABC
from typing import Any


class AbstractView:  # pragma: no cover
    def realize(self) -> Any:
        raise NotImplementedError


class ContainerView(AbstractView, ABC):  # pragma: no cover
    def add_child(self, view: AbstractView):
        raise NotImplementedError


class ListView(AbstractView, ABC):  # pragma: no cover
    def add(self, view: AbstractView):
        raise NotImplementedError

    def remove(self, view: AbstractView):
        raise NotImplementedError


class ChoiceView(AbstractView, ABC):  # pragma: no cover
    def set_view(self, view: AbstractView):
        raise NotImplementedError
