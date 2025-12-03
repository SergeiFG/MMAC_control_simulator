import logging

from numbers import Number
import copy

from basics import FunctionalBlock, FunctionalBlockBank


class Supervisor:

    def __init__(self, logger: logging.Logger,
                 name: str = "",
                 controller_bank: FunctionalBlockBank = None,
                 estimator_bank: FunctionalBlockBank = None,
                 *args,
                 **kwargs):

        self.logger = logger

        if name == "":
            self.logger.warning(f"Не задано имя супервизора")
        self.name = name

        self.logger.info(f"Инициализация супервизора {name}")
        self.logger.debug(f"Банк контроллеров: {controller_bank}")
        self.logger.debug(f"Банк эстиматоров: {estimator_bank}")

        if controller_bank is None:
            self.logger.error(f"Не задан банк контроллеров для супервизора {self.name}")
        else:
            self.controller_bank = controller_bank

        if estimator_bank is None:
            self.logger.error(f"Не задан банк эстиматоров для супервизора {self.name}")
        else:
            self.estimator_bank = estimator_bank

        self.last_switch: Number = None  # TODO: Точно ли супервайзеру нужно это знать?
        self.current_controller: str = None
        self.current_estimator: str = None

        self.estimators_backup = None
        self.controllers_backup = None

    def choose_controller(self) -> None:
        raise NotImplementedError

    def chose_estimator(self) -> None:
        raise NotImplementedError

    def compute_estimators(self,
                           tick_duration: Number | dict[str, Number],
                           names: list[str] | None = None,
                           time_for_not_specified: Number = None,
                           save_backup: bool = False) -> None:

        if save_backup:
            self.estimators_backup = copy.deepcopy(self.estimator_bank)
        self.estimator_bank.compute(tick_duration, names, time_for_not_specified)

    def compute_controllers(self,
                           tick_duration: Number | dict[str, Number],
                           names: list[str] | None = None,
                           time_for_not_specified: Number = None,
                            save_backup: bool = False) -> None:

        if save_backup:
            self.controllers_backup = copy.deepcopy(self.controller_bank)
        self.controller_bank.compute(tick_duration, names, time_for_not_specified)

    def revert_estimators(self) -> None:
        if self.estimators_backup is None:
            self.logger.warning(f"Попытка вернуть бэкап эстиматоров, но он пуст, супервизор {self.name}")
        else:
            self.estimator_bank = copy.deepcopy(self.estimators_backup)

    def revert_controllers(self) -> None:
        if self.controllers_backup is None:
            self.logger.warning(f"Попытка вернуть бэкап контроллеров, но он пуст, супервизор {self.name}")
        else:
            self.controller_bank = copy.deepcopy(self.controllers_backup)


if __name__ == '__main__':
    from Parameters import Parameter, DerivedParameter, ParameterSet
    model_params_1 = ParameterSet(
        x1=Parameter("x1", 4, sensor=True, max_value=5),
        x2=Parameter("x2", 5, sensor=True),
        y1=DerivedParameter("y1", lambda x1, x2: x1 ** 2 + x2, ["x1", "x2"], units='m2'),
        y2=DerivedParameter("y2", lambda x: x * 2, ["y3"]),
        y3=DerivedParameter("y3", lambda x: x * 2, ["y1"], sensor=True, sensor_noise=lambda x: x + 1)
    )
    model_params_2 = ParameterSet(
        x1=Parameter("x1", 4, sensor=True, max_value=5),
        x2=Parameter("x2", 5, sensor=False),
        y1=DerivedParameter("y1", lambda x1, x2: x1 + x2**2, ["x1", "x2"], units='m2'),
        )
    model_params_3 = ParameterSet(
        x1=Parameter("x1", 4, sensor=True, max_value=5),
        x2=Parameter("x2", 5, sensor=False),
        y1=DerivedParameter("y1", lambda x1, x2: x1 + x2, ["x1", "x2"], units='m2'),
    )
    logger = logging.getLogger(__name__)
    model_1 = FunctionalBlock(logger, model_params_1, name="model 1")
    model_2 = FunctionalBlock(logger, model_params_2, name="model 2")
    model_3 = FunctionalBlock(logger, model_params_3, name="model 3")
    model_bank_1 = FunctionalBlockBank(logger=logger, model_set=[model_1, model_2], name="controller model_bank")
    model_bank_2 = FunctionalBlockBank(logger=logger, model_set=[model_3], name="estimator model bank")
    supervisor = Supervisor(logger=logger, name="test supervisor", controller_bank=model_bank_1, estimator_bank=model_bank_2)
    print(supervisor.controller_bank.get_state())
    supervisor.compute_controllers(tick_duration=1, save_backup=True)
    supervisor.controller_bank.load_variables(d={'x2':0})
    print(supervisor.controller_bank.get_state())
    supervisor.revert_controllers()
    print(supervisor.controller_bank.get_state())
