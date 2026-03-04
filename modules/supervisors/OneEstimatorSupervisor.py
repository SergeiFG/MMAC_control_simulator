from basics import Estimator, FunctionalBlock, FunctionalBlockBank, Parameter, ParameterSet, Supervisor
from numbers import Number
import logging


class OneEstimatorSupervisor(Supervisor):
    """
    Версия супервизора с одним эстиматором и заранее прописанной логикой выбора контроллера
    """
    def __init__(self, logger: logging.Logger,
                 name: str = "Supervisor",
                 controllers: list[FunctionalBlock] = None,
                 estimators: list[Estimator] = None,
                 *args,
                 **kwargs):
        """

        :param logger:  Логгер для записи и вывода процесса работы
        :param name: Имя супервизора, задано по умолчанию
        :param controllers: Массив требуемых контроллеров
        :param estimators: Эстиматор, который будет использоваться
        :param args:
        :param kwargs:
        """
        if len(estimators) != 1:
            raise AttributeError(f"Для Супервизора с одним эстиматором задано неверное число эстиматоров")

        super().__init__(logger=logger,
                         name=name,
                         controllers=controllers,
                         estimators=estimators,
                         *args,
                         **kwargs)

    def choose_controller(self) -> None:
        """
        Выбирает контроллер, для которого у эстиматора максимальное значение quality
        :return:
        """
        estimator = self.estimator_bank[self.current_estimator]
        controller_quality = estimator.read_sensors()
        chosen_controller = max(controller_quality, key=controller_quality.get)  # имя (ключ) с максимальным значением
        self.current_controller = chosen_controller

    def chose_estimator(self) -> None:
        self.current_estimator = self.estimator_bank.get_names()[0]