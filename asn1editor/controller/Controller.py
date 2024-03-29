from typing import Optional, Any, Dict, List, Tuple, Union

from asn1editor.controller import Converter
from asn1editor.interfaces.BitstringInterface import BitstringInterface
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface


class Controller:
    """
    The controller serves to connect the GUI representation with the data model.

    It manages the path of elements to be able to access elements by a dot separated name.
    """

    def __init__(self, name: str, parent: 'Controller', optional_interface: Optional[OptionalInterface]):
        self._name = name
        self._parent = parent
        self._optional_interface = optional_interface
        if self._optional_interface:
            self._optional_interface.set_has_value(self._optional_interface.get_default_has_value())
        self.path = ''
        if parent is not None:
            parent.add_controller(name, self)

            parent_path = self._parent.get_path()
            self.path = self._name
            if len(parent_path):
                self.path = self._parent.get_path() + '.' + self.path

    def add_controller(self, name: str, other: 'Controller'):
        """
        Adds a controller with a given name. This is used when an element supports dynamic instantiation of sub-elements (like lists or choices).
        The function is called by child controllers to tell their parents about their existence.
        """
        raise NotImplementedError()

    def model_to_view(self, model: Dict[str, Any]):
        """
        Sets the values from the model to the views
        """
        raise NotImplementedError()

    def view_to_model(self) -> Optional[Dict[str, Any]]:
        """
        Gets the values from the view and puts them in a model
        """
        raise NotImplementedError()

    def event_handler(self):
        """
        Handles an event that involves creation or removal of sub-controllers like changing the number of list elements or changing a choice.

        Is called when the value of the element changes.
        """
        pass

    def optional_handler(self):
        """
        Handles the change of the optional status of an element.
        """
        pass

    def _model_to_view_optional(self, model: Dict[str, Any]):
        has_value = self._name in model or isinstance(self._parent, ListController) or isinstance(self._parent, ChoiceController)
        assert has_value or self._optional_interface, f'Value for {self.path} not in data'
        if self._optional_interface:
            # Notify view if value is there or not
            self._optional_interface.set_has_value(has_value)
        return has_value

    def _view_to_model_optional(self):
        return not self._optional_interface or self._optional_interface.get_has_value()

    def get_path(self) -> str:
        return self.path

    def __repr__(self):
        return self._name


class ValueController(Controller):
    """
    Controller for plain value fields.

    A value controller uses a data converter to perform the mapping between values provided from a view and those expected in the model.
    """

    def __init__(self, name: str, parent: Controller, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface],
                 data_converter: Converter.Converter):
        super().__init__(name, parent, optional_interface)
        self._value_interface = value_interface
        self._data_converter = data_converter
        self._default = self._data_converter.default()
        self._set_value(self._default)

    def add_controller(self, name: str, other: Controller):
        raise Exception('ValueController cannot add a controller')

    def model_to_view(self, model: Union[Dict[str, Any], Any]):
        if isinstance(model, Dict):
            if self._model_to_view_optional(model):
                self._set_value(model[self._name])
        else:
            self._set_value(model)

    def view_to_model(self) -> Any:
        if self._view_to_model_optional():
            return self._data_converter.from_view(self._value_interface.get_value())

    def _set_value(self, value: Any):
        self._value_interface.set_value(self._data_converter.to_view(value))


class BoolController(Controller):
    """
    A bool controller manages a single boolean element.
    """

    def __init__(self, name: str, parent: Controller, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface], default: bool):
        super().__init__(name, parent, optional_interface)
        self._value_interface = value_interface
        self._default = default if default is not None else False
        self._value_interface.set_value(self._default)

    def add_controller(self, name: str, other: Controller):
        raise Exception('ValueController cannot add a controller')

    def model_to_view(self, model: Union[Dict[str, Any], Any]):
        if isinstance(model, Dict):
            if self._model_to_view_optional(model):
                self._value_interface.set_value(model[self._name])
        else:
            self._value_interface.set_value(model)

    def view_to_model(self) -> bool:
        if self._view_to_model_optional():
            return self._value_interface.get_value()


class ListController(Controller):
    """
    A list controller manages a list of elements with the same type. The number of elements may be dynamic and a factory is provided to create or destroy new
    instances of the list. This factory creates both the views and the controllers for a new element.
    """

    def __init__(self, name: str, parent: Controller, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface], list_instance_factory,
                 default: int):
        super().__init__(name, parent, optional_interface)
        self._value_interface = value_interface
        self._controllers = []
        self._list_instance_factory = list_instance_factory
        if default is not None and default > 0 and not optional_interface:
            self._value_interface.set_value(str(default))
            self.event_handler()

    def add_controller(self, name: str, other: Controller):
        self._controllers.append(other)

    def model_to_view(self, model: Union[List[Any], Dict[str, Any]]):
        if self._model_to_view_optional(model):
            if isinstance(model, Dict):
                model: List = model[self._name]
            new_num = len(model)
            self.__sync_controllers(new_num)
            for i, controller in enumerate(self._controllers):
                controller.model_to_view(model[i])
            self._value_interface.set_value(str(new_num))
        else:
            self.__sync_controllers(0)

    def view_to_model(self) -> Optional[List]:
        if self._view_to_model_optional():
            model = []
            for controller in self._controllers:
                model.append(controller.view_to_model())
            return model

    def event_handler(self):
        new_num = int(self._value_interface.get_value())
        self.__sync_controllers(new_num)

    def optional_handler(self):
        if not self._optional_interface.get_has_value():
            self.__sync_controllers(0)
        else:
            self.event_handler()

    def __sync_controllers(self, new_num: int):
        if new_num > len(self._controllers):
            prev_num = len(self._controllers)
            for i in range(prev_num, new_num):
                self._list_instance_factory.create(i, self)
        else:
            for i in reversed(range(new_num, len(self._controllers))):
                # First, delete the view
                self._list_instance_factory.destroy(i)
                # And finally destroy the controller
                del self._controllers[i]


class ChoiceController(Controller):
    """
    A choice may contain a selection of different sub-elements. The controller creates the
    """

    def __init__(self, name: str, parent: Controller, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface], choice_instance_factory,
                 default: str):
        super().__init__(name, parent, optional_interface)
        self._value_interface = value_interface
        self._controller: Optional[Controller] = None
        self._choice_instance_factory = choice_instance_factory
        self._value_interface.set_value(default)
        self._choice_instance_factory.create(default, self)

    def add_controller(self, name: str, other: 'Controller'):
        self._controller = other

    def model_to_view(self, model: Dict[str, Any]):
        if self._model_to_view_optional(model):
            choice = model[self._name][0]
            self._value_interface.set_value(choice)
            self._choice_instance_factory.create(choice, self)
            self._controller.model_to_view(model[self._name][1])

    def view_to_model(self) -> Optional[Tuple[str, Any]]:
        if self._view_to_model_optional():
            return self._value_interface.get_value(), self._controller.view_to_model()

    def event_handler(self):
        choice = self._value_interface.get_value()
        self._choice_instance_factory.create(choice, self)


class BitstringController(Controller):
    def __init__(self, name: str, parent: Optional[Controller], bitstring_interface: BitstringInterface,
                 optional_interface: Optional[OptionalInterface], number_of_bits: int):
        super().__init__(name, parent, optional_interface)
        self._bitstring_interface = bitstring_interface
        self._number_of_bits = number_of_bits

    def add_controller(self, name: str, other: Controller):
        raise Exception('ValueController cannot add a controller')

    def model_to_view(self, model: Dict[str, Any]):
        if self._model_to_view_optional(model):
            values = []
            bytes_, num_bits = model[self._name]
            assert num_bits == self._number_of_bits
            for bit in range(self._number_of_bits):
                bit_index = bit % 8
                byte_index = bit // 8
                if bytes_[byte_index] & (1 << bit_index):
                    values.append(bit)
            self._bitstring_interface.set_values(values)

    def view_to_model(self) -> Optional[Tuple[bytes, int]]:
        if self._view_to_model_optional():
            bytes_ = bytearray(b'\x00' * -(-self._number_of_bits // 8))
            values = self._bitstring_interface.get_values()
            for bit in values:
                bit_index = bit % 8
                byte_index = bit // 8
                bytes_[byte_index] |= (1 << bit_index)

            return bytes_, self._number_of_bits


class ContainerController(Controller):
    def __init__(self, name: str, parent: Optional[Controller], optional_interface: Optional[OptionalInterface]):
        super().__init__(name, parent, optional_interface)
        self._controllers: Dict[str, Controller] = {}

    def add_controller(self, name: str, other: Controller):
        self._controllers[name] = other

    def model_to_view(self, model: Dict[str, Any]):
        if self._model_to_view_optional(model):
            if isinstance(self._parent, ListController) or isinstance(self._parent, ChoiceController):
                self._model_to_view(model)
            else:
                self._model_to_view(model[self._name])

    def view_to_model(self) -> Optional[Dict[str, Any]]:
        if self._view_to_model_optional():
            return self._view_to_model()

    def _model_to_view(self, model: Dict[str, Any]):
        for name, controller in self._controllers.items():
            controller.model_to_view(model)

    def _view_to_model(self) -> Dict[str, Any]:
        model = {}
        for name, controller in self._controllers.items():
            sub_model = controller.view_to_model()
            if sub_model is not None or isinstance(controller, NullController):
                model[name] = sub_model
        return model


class NullController(Controller):

    def add_controller(self, name: str, other: 'Controller'):
        raise Exception('NullController cannot add a controller')

    def model_to_view(self, model: Dict[str, Any]):
        pass

    def view_to_model(self) -> Optional:
        return None


class RootController(ContainerController):
    def __init__(self, name: str):
        super().__init__(name, None, None)

    def model_to_view(self, model: Dict[str, Any]):
        self._model_to_view(model)

    def view_to_model(self) -> Optional[Dict[str, Any]]:
        return self._view_to_model()
