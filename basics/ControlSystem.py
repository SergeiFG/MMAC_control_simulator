import logging

from basics import Parameter, DerivedParameter, ParameterSet

from numbers import Number
import copy

from basics import FunctionalBlock, FunctionalBlockBank, Supervisor


class ControlSystem(FunctionalBlock):

    def __init__(self,
                 logger: logging.Logger,
                 parameters: ParameterSet,
                 name: str = "",
                 supervisor: Supervisor = None,
                 control_action_keys: list[str] = None):
        super().__init__(logger=logger, parameters=parameters, name=name)
        self.logger.info(f"Инициализация системы управления {self.name}")

        self.control_actions = None

        if supervisor is None:
            self.logger.error(f"Супервизор не задан для {self.name}")
            raise ValueError("supervisor None при инициализации системы управления")
        else:
            self.logger.debug(f"Супервизор {supervisor}")
            self.supervisor = supervisor

        if control_action_keys is None:
            self.logger.error(f"Не заданы требуемые управляющие воздействия для {self.name}")
            raise ValueError("control_actions None при инициализации системы управления")
        else:
            self.logger.debug(f"Управляющие воздействия {control_action_keys}")
            self.control_action_keys = control_action_keys

    def compute(self, tick_duration:Number = None, **kwargs) -> None:
        self.logger.info(f"Начинаем цикл работы системы управления {self.name}")
        self.logger.debug(f"Период симуляции системы управления {tick_duration}")

        self.logger.info(f"Начинаем работу с банком эстиматоров системы управления {self.name}")
        self.supervisor.compute_estimators(tick_duration=tick_duration, save_backup=True, **kwargs)
        self.supervisor.chose_estimator()
        self.supervisor.revert_estimators()
        self.logger.info(f"Итоговый эстиматор {self.supervisor.current_estimator}")

        self.logger.info(f"Начинаем работу с банком контроллеров системы управления {self.name}")
        self.supervisor.compute_controllers(tick_duration=tick_duration, save_backup=True, **kwargs)
        self.supervisor.choose_controller()
        self.supervisor.revert_controllers()
        self.logger.info(f"Итоговый контроллер {self.supervisor.current_controller}")

        self.logger.info(f"Начинаем вычисление управляющих воздействий {self.name}")
        controller = copy.deepcopy(self.supervisor.controller_bank[self.supervisor.current_controller])
        controller.compute(tick_duration=tick_duration)
        self.control_actions = controller.read_sensors(keys=self.control_action_keys)
        self.logger.info(f"Итоговые управляющие воздействия {self.control_actions}")

    def read_control_actions(self):
        return self.control_actions

    def load_sensor_data(self, data: dict[str, Number]) -> None:
        self.logger.info(f"Загружаем данные с сенсоров в систему управления {self.name}")
        self.logger.debug(f"Данные с сенсоров {data}")

        self.supervisor.estimator_bank.load_variables(data=data)
        self.supervisor.controller_bank.load_variables(data=data)

