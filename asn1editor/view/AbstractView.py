from abc import ABC
from typing import Any


class AbstractView:
    def realize(self) -> Any:
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError


class ContainerView(AbstractView, ABC):
    def add_child(self, view: AbstractView):
        raise NotImplementedError


class ListView(AbstractView, ABC):
    def add(self, view: AbstractView):
        raise NotImplementedError

    def remove(self, view: AbstractView):
        raise NotImplementedError


class ChoiceView(AbstractView, ABC):
    def set_view(self, view: AbstractView):
        raise NotImplementedError
