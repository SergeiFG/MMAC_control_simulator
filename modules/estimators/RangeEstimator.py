from basics import Estimator, FunctionalBlockBank, Parameter, ParameterSet
from numbers import Number
import logging


class RangeEstimator(Estimator):
    """
    Реализация эстиматора через диапазоны параметров процесса.

    controller_regions формат:
    {
        "controller_name": {
            "process_param_name": (min, max),
            ...
        },
        ...
    }

    - границы задаются как [min, max), где None = -inf или +inf в зависимости от позиции, верхняя граница строгая, нижняя нестрогая;
    - область каждого контроллера должна содержать границы по всем параметрам процесса;
    - в рабочей точке должен быть найден ровно один контроллер.
    """

    def __init__(
        self,
        logger: logging.Logger,
        process_parameters: list[str],
        controller_bank: FunctionalBlockBank | None = None,
        extra_parameters: list[str] | None = None,
        name: str = "Estimator",
        controller_regions: dict[str, dict[str, tuple[Number | None, Number | None]]] = None,
        *args,
        **kwargs,
    ):
        """
        :param logger: логгер для записи ошибок и дебага
        :param process_parameters: массив имён параметров, должен совпадать с аналогичными в модели процесса
        :param controller_bank: банк контроллеров для сбора имён контроллеров, не заполняем, автоматический
        :param controller_regions: границы для каждого контроллера для каждого параметра, задаются в виде
            {
            "controller_name": {
                "process_param_name": (min, max),
                ...
            },
            ...
        }
        границы задаются как (min, max), где None = -inf или +inf в зависимости от позиции.

        :param extra_parameters: дополнительные параметры, поставить при необходимости
        :param name: имя эстиматора, не менять
        """

        self.controller_regions = controller_regions
        super().__init__(
            logger=logger,
            process_parameters=process_parameters,
            controller_bank=controller_bank,
            extra_parameters=extra_parameters,
            name=name,
            *args,
            **kwargs,
        )

    def update_controllers(self, controller_bank: FunctionalBlockBank) -> None:
        super().update_controllers(controller_bank=controller_bank)
        self._validate_regions()

    def _validate_regions(self) -> None:
        """Проверка, что все заданные регионы заполнены верно"""
        if self.controller_regions is None:
            self.logger.error(f"Не заданы области для эстиматора: {self.name}")
            raise ValueError(f"Не заданы области для контроллеров: {self.name}")

        controller_names = set(self.controller_names)
        region_names = set(self.controller_regions.keys())

        missing_regions = controller_names - region_names
        if missing_regions:
            self.logger.error(f"Не заданы области для контроллеров: {sorted(missing_regions)}")
            raise ValueError(f"Не заданы области для контроллеров: {sorted(missing_regions)}")

        unknown_regions = region_names - controller_names
        if unknown_regions:
            self.logger.error(f"Заданы области для неизвестных контроллеров: {sorted(unknown_regions)}")
            raise ValueError(f"Заданы области для неизвестных контроллеров: {sorted(unknown_regions)}")

        process_keys = set(self.process_parameter_names)
        for controller_name, region in self.controller_regions.items():
            region_keys = set(region.keys())
            if region_keys != process_keys:
                self.logger.error(
                    f"Для контроллера {controller_name} область должна быть задана "
                    f"для всех параметров процесса: {sorted(process_keys)}, получено: {sorted(region_keys)}")
                raise ValueError(
                    f"Для контроллера {controller_name} область должна быть задана"
                )

            for parameter_name, bounds in region.items():
                if len(bounds) != 2:
                    self.logger.error(f"Неверная размерность границ для {controller_name}.{parameter_name} - {bounds}")
                    raise ValueError(
                        f"Границы параметра {controller_name}.{parameter_name} для контроллера {controller_name} "
                        f"должны быть кортежем (min, max)"
                    )

                lower, upper = bounds
                if lower is not None and upper is not None and lower > upper:
                    self.logger.error(f"Некорректный диапазон для {controller_name}.{parameter_name}: ({lower}, {upper})")
                    raise ValueError(f"Некорректный диапазон для {controller_name}.{parameter_name}: ({lower}, {upper})")

    @staticmethod
    def _is_inside(value: Number, bounds: tuple[Number | None, Number | None]) -> bool:
        lower, upper = bounds
        if lower is not None and value < lower:
            return False
        if upper is not None and value >= upper:
            return False
        return True

    def _find_matching_controllers(self) -> list[str]:
        matched = []

        for controller_name, region in self.controller_regions.items():
            is_inside_region = True
            for parameter_name, bounds in region.items():
                if not self._is_inside(self.parameters[parameter_name], bounds):
                    is_inside_region = False
                    break
            if is_inside_region:
                matched.append(controller_name)

        return matched

    def select_controller(self) -> str:
        matched_controllers = self._find_matching_controllers()

        if len(matched_controllers) == 0:
            self.logger.error(f"Для точки {self.parameters.as_dict(self.process_parameter_names)} не найдено ни одного контроллера")
            raise ValueError(
                "Текущая точка процесса не попала ни в одну область. "
                "Проверьте разбиение пространства параметров на области контроллеров."
            )

        if len(matched_controllers) > 1:
            self.logger.warning(
                f"Для точки {self.parameters.as_dict(self.process_parameter_names)} найдено более одного контроллера: "
                f"{matched_controllers}")
            raise RuntimeWarning(
                "Текущая точка процесса попала сразу в несколько областей. "
                "Границы контроллеров должны формировать непересекающиеся области. "
                f"Совпавшие контроллеры: {matched_controllers}"
            )

        return matched_controllers[0]