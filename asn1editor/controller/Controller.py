from typing import Optional, Any, Dict, List, Tuple, Union

from asn1editor.controller import Converter
from asn1editor.interfaces.OptionalInterface import OptionalInterface
from asn1editor.interfaces.ValueInterface import ValueInterface


class Controller:
    def __init__(self, name: str, parent: 'Controller', optional_interface: Optional[OptionalInterface]):
        self._name = name
        self._parent = parent
        self._optional_interface = optional_interface
        if self._optional_interface:
            self._optional_interface.set_has_value(False)
        if parent is not None:
            parent.add_controller(name, self)

    def add_controller(self, name: str, other: 'Controller'):
        raise NotImplementedError()

    def model_to_view(self, model: Dict[str, Any]):
        raise NotImplementedError()

    def view_to_model(self) -> Optional[Dict[str, Any]]:
        raise NotImplementedError()

    def event_handler(self):
        pass

    def optional_handler(self):
        pass

    def _model_to_view_optional(self, model: Dict[str, Any]):
        has_value = self._name in model or isinstance(self._parent, ListController)
        assert has_value or self._optional_interface
        if self._optional_interface:
            # Notify view if value is there or not
            self._optional_interface.set_has_value(has_value)
        return has_value

    def _view_to_model_optional(self):
        return not self._optional_interface or self._optional_interface.get_has_value()

    def __repr__(self):
        return self._name


class ValueController(Controller):
    def __init__(self, name: str, parent: Controller, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface],
                 data_converter: Converter.Converter, default: Optional[Any]):
        super().__init__(name, parent, optional_interface)
        self._value_interface = value_interface
        self._data_converter = data_converter
        self._default = default if default is not None else self._data_converter.from_str('')
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
            return self._data_converter.from_str(self._value_interface.get_value())

    def _set_value(self, value: Any):
        self._value_interface.set_value(self._data_converter.to_str(value))


class BoolController(Controller):
    def __init__(self, name: str, parent: Controller, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface], default: bool):
        super().__init__(name, parent, optional_interface)
        self._value_interface = value_interface
        self._default = default if default is not None else False
        self._value_interface.set_value(str(self._default))

    def add_controller(self, name: str, other: Controller):
        raise Exception('ValueController cannot add a controller')

    def model_to_view(self, model: Dict[str, Any]):
        if self._model_to_view_optional(model):
            self._value_interface.set_value(str(model[self._name]))

    def view_to_model(self) -> bool:
        if self._view_to_model_optional():
            return self._value_interface.get_value().lower() in ['true', '1']


class ListController(Controller):
    def __init__(self, name: str, parent: Controller, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface], list_instance_factory, default: int):
        super().__init__(name, parent, optional_interface)
        self._value_interface = value_interface
        self._controllers = []
        self._list_instance_factory = list_instance_factory
        if default > 0:
            self._value_interface.set_value(str(default))
            self.event_handler()

    def add_controller(self, name: str, other: Controller):
        self._controllers.append(other)

    def model_to_view(self, model: Dict[str, Any]):
        if self._model_to_view_optional(model):
            model: List = model[self._name]
            new_num = len(model)
            self.__sync_controllers(new_num)
            for i, controller in enumerate(self._controllers):
                controller.model_to_view(model[i])
            self._value_interface.set_value(str(new_num))
        else:
            self._value_interface.set_value('0')
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
            self._value_interface.set_value('0')
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
    def __init__(self, name: str, parent: Controller, value_interface: ValueInterface, optional_interface: Optional[OptionalInterface], default: str,
                 choice_instance_factory):
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
            self._choice_instance_factory.create(choice, self)
            self._controller.model_to_view(model[self._name][1])

    def view_to_model(self) -> Optional[Tuple[str, Any]]:
        if self._view_to_model_optional():
            return self._value_interface.get_value(), self._controller.view_to_model()

    def event_handler(self):
        choice = self._value_interface.get_value()
        self._choice_instance_factory.create(choice, self)


class ContainerController(Controller):
    def __init__(self, name: str, parent: Optional[Controller], optional_interface: Optional[OptionalInterface]):
        super().__init__(name, parent, optional_interface)
        self._controllers: Dict[str, Controller] = {}

    def add_controller(self, name: str, other: Controller):
        self._controllers[name] = other

    def model_to_view(self, model: Dict[str, Any]):
        if self._model_to_view_optional(model):
            if not isinstance(self._parent, ListController):
                self._model_to_view(model[self._name])
            else:
                self._model_to_view(model)

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
            if sub_model is not None:
                model[name] = sub_model
        return model


class RootController(ContainerController):
    def __init__(self, name: str):
        super().__init__(name, None, None)

    def model_to_view(self, model: Dict[str, Any]):
        self._model_to_view(model)

    def view_to_model(self) -> Optional[Dict[str, Any]]:
        return self._view_to_model()
