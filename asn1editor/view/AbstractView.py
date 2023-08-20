from abc import ABC
from typing import Any


class AbstractView:  # pragma: no cover
    """
    Abstract representation of a view
    """

    def realize(self) -> Any:
        """
        @return: Class that contains the concrete view setup to the current state of the model
        """
        raise NotImplementedError


class ContainerView(AbstractView, ABC):  # pragma: no cover
    """
    Abstract container view allowing to add children
    """

    def add_child(self, view: AbstractView):
        """
        Adds another abstract view as child of the container. Called while building the container.
        """
        raise NotImplementedError


class ListView(AbstractView, ABC):  # pragma: no cover
    """
    Abstract list view allowing to add and remove list elements
    """

    def add(self, view: AbstractView):
        """
        Appends one more list element. Called whenever the list changes.
        """
        raise NotImplementedError

    def remove(self, view: AbstractView):
        """
        Removes the last list element. Called whenever the list changes.
        """
        raise NotImplementedError


class ChoiceView(AbstractView, ABC):  # pragma: no cover
    """
    Abstract choice view allowing to replace the choice element view
    """

    def set_view(self, view: AbstractView):
        """
        Replaces the choice element view
        """
        raise NotImplementedError
