import logging
from numbers import Number

from basics.FunctionalBlock import FunctionalBlock
from basics.FunctionalBlockBank import FunctionalBlockBank
from basics.Parameters import Parameter, ParameterSet


class Estimator(FunctionalBlock):
    """
    Базовый эстиматор.

    Входные данные:
    - параметры процесса - массив имён параметров, должен совпадать с аналогичными в модели процесса;
    - принимает controller_bank и автоматически добавляет сенсоры качества по именам контроллеров;
    - позволяет добавить дополнительные параметры через `extra_parameters` или переопределение
      `build_additional_parameters` в наследниках;
    - `compute` делегирует выбор контроллера в `select_controller`, который реализуется
      конкретной стратегией.
    """

    def __init__(
        self,
        logger: logging.Logger,
        process_parameters: list[str],
        controller_bank: FunctionalBlockBank | None = None,
        extra_parameters: list[str] = None,
        name: str = "Estimator",
        *args,
        **kwargs,
    ):
        self.controller_names = controller_bank.get_names() if controller_bank is not None else []
        self.extra_parameters = extra_parameters if extra_parameters is not None else []

        self.process_parameter_names = process_parameters

        parameters = self._build_parameter_set(
            process_parameters=self.process_parameter_names,
            controller_names=self.controller_names,
            extra_parameters=self.extra_parameters
        )
        super().__init__(logger=logger, parameters=parameters, name=name, *args, **kwargs)

    def update_controllers(self, controller_bank: FunctionalBlockBank) -> None:
        """
        Метод обновления параметров Эстиматора - добавляет к набору параметров дополнительные параметры на каждый контроллер
        :param controller_bank: Набор контроллеров, для которых требуется подготовить параметры
        :return:
        """
        self.controller_names = controller_bank.get_names()

        new_params = {}
        for controller_name in self.controller_names:
            new_params[controller_name] = Parameter(
                name=f"{controller_name} quality",
                value=0,
                sensor=True,
                min_value=0,
                max_value=1,
            )

        self.update_params(ParameterSet(**new_params))

    @staticmethod
    def _build_parameter_set(
        process_parameters: list[str],
        controller_names: list[str],
        extra_parameters: list[str] | None = None,

    ) -> ParameterSet:
        """

        :param process_parameters:  параметры процесса, по ним формируется пространство динамики (состояния установки)
        :param extra_parameters: дополнительные параметры, поставить при необходимости
        :return: ParameterSet набор параметров для работы данного эстиматора
        """

        params = {}

        for controller_name in controller_names:
            params[controller_name] = Parameter(
                name=f"{controller_name} quality",
                value=0,
                sensor=True,
                min_value=0,
                max_value=1,
            )
        for parameter_name in process_parameters + extra_parameters:
            params[parameter_name] = Parameter(
                name=f"{parameter_name}",
                value=0,
                sensor=False
            )

        return ParameterSet(**params)

    def select_controller(self) -> str:
        """Стратегия выбора контроллера. Должна быть реализована в наследнике."""
        raise NotImplementedError

    def compute(self, tick_duration: Number = None) -> None:
        active_controller = self.select_controller()

        if active_controller not in self.controller_names:
            raise ValueError(
                f"Выбран неизвестный контроллер {active_controller}. "
                f"Доступные контроллеры: {self.controller_names}"
            )

        for controller_name in self.controller_names:
            self.parameters[controller_name] = 1 if controller_name == active_controller else 0



