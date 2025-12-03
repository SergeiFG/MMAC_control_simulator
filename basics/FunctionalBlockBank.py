import logging

from numbers import Number
from typing import Set

from basics import FunctionalBlock


class FunctionalBlockBank:
    """
    FunctionalBlockBank
    ---
    Базовый класс для банков функциональных блоков, может быть использован для банка контроллеров или эстиматоров.

    """

    def __init__(self, logger: logging.Logger, model_set: list[FunctionalBlock], name: str = "") -> None:
        """
        __init__
        ---
        Аргументы:
            logger: logging.Logger                  - Логгер для записи логов в файл и консоль
            model_set: list[FunctionalBlock]        - Набор блоков для данного набора
            name: str = ""                          - Имя данного набора функциональных блоков
        """
        self.logger = logger
        self.model_set = model_set
        self.name = name

        self.logger.info(f"Инициализация набора функциональных блоков {self.name} : {[block.name for block in self.model_set]}")

        try:
            self._dict_model_set = {block.name: block for block in self.model_set}
            self.logger.debug(f"Словарь функциональных блоков успешно создан для {self.name}")
        except Exception as e:
            self.logger.error(f"Ошибка создания словаря функциональных блоков для {self.name}, имена не уникальные")
            raise e

        self._variables = self._collect_variables() # Пока без применения, может понадобится потом
        self._sensors = self._collect_sensors()
        self.logger.info(f"Найдены следующие входные переменные для набора {self.name}: {self._variables}")

    def _collect_variables(self) -> Set[str]:
        """
        _collect_variables
        ---
        Метод для сбора всех входных переменных всех блоков в наборе
        """
        tmp = []
        for block in self.model_set:
            tmp += block.variables
        return set(tmp)

    def _collect_sensors(self) -> Set[str]:
        tmp = []
        for block in self.model_set:
            tmp += block.sensors
        return set(tmp)

    def load_variables(self, data: dict[str, Number], names:list[str] | None = None) -> None:
        """
        load_varibles
        ---
        Метод загрузки всех или части значений в виде словаря dict[str, Number] во все или часть блоков из набора

        Аргументы:
            d: dict[str, Number]            - Словарь с переменными и их значениями для загрузки
            names:list[str] | None = None   - Массив имён блоков, из которых нужно выгрузить значения параметров, если не задан, то выгружаются все
        """

        self.logger.info(f"Начато обновление функциональных блоков в наборе {self.name}")
        self.logger.debug(f"Для обновления использованы значения {data}")
        self.logger.debug(f"Для обновления использованы блоки {names}")
        if names is None:
            names = self._dict_model_set.keys()

        for block_name in names:
            self.logger.debug(f"Обрабатываем модель {block_name}")
            if block_name not in self._dict_model_set.keys():
                self.logger.error(f"Попытка записать значения в несуществующий в наборе {self.name} функциональный блок {block_name}")
                raise KeyError
            dict_to_load = {key: value for key, value in data.items() if key in self[block_name].variables}
            self[block_name].load_variables(dict_to_load)

    def read_sensors(self, variables: list[str] = None, names:list[str] | None = None) -> dict[str, dict[str, Number]]:
        """
        read_sensors
        ---
        Метод выгрузки всех или части значений сенсоров набора функциональных блоков в виде словаря dict[str, dict[str, Number]]
        Ключи - имена функциональных блоков в наборе, значения - словари типа {имя параметра: значение}
        Используется для считывания состояния модели для архива.
        Аргументы:
            keys: list[str] = None      - Массив ключей при необходимости ограничивает выгружаемые параметры, если не задан, выгружаются все
            names: list[str] = None     - Массив имён блоков, из которых нужно выгрузить значения параметров, если не задан, то выгружаются все
        """

        self.logger.info(f"Начат сбор данных сенсоров по функциональным блокам в наборе {self.name}")
        self.logger.debug(f"Ищем значения значения {variables}")
        self.logger.debug(f"Ищем блоки {names}")

        if names is None:
            names = self._dict_model_set.keys()

        if variables is None:
            variables = self._sensors
            skip_warning_unexpected_variables = True
        else:
            skip_warning_unexpected_variables = False

        res = {}
        for block_name in names:
            self.logger.debug(f"Обрабатываем модель {block_name}")

            if block_name not in self._dict_model_set.keys():
                self.logger.error(
                    f"Попытка считать значения из несуществующего блока в наборе {self.name} функциональный блок {block_name}")
                raise KeyError

            sensors_to_read = list(set(variables) & set(self[block_name].sensors)) # Берём только те элементы, которые есть в перечне сенсоров блока
            difference = list(set(variables).difference(sensors_to_read))
            if difference and not skip_warning_unexpected_variables:
                self.logger.warning(f"Для блока {block_name} запрошены несуществующие сенсоры {difference}")

            res[block_name] = self[block_name].read_sensors(sensors_to_read)

        return res

    def get_state(self, keys: list[str] = None, names: list[str] | None = None) -> dict[str, dict[str, Number | str]]:
        """
        get_state
        ---
        Метод выгрузки всех или части значений набора функциональных блоков в виде словаря dict[str, dict[str, Number]]
        Ключи - имена функциональных блоков в наборе, значения - словари типа {имя параметра: значение}
        Используется для считывания состояния модели для архива.
        Аргументы:
            keys: list[str] = None      - Массив ключей при необходимости ограничивает выгружаемые параметры, если не задан, выгружаются все
            names: list[str] = None     - Массив имён блоков, из которых нужно выгрузить значения параметров, если не задан, то выгружаются все
        """

        self.logger.info(f"Начат сбор данных состояния по функциональным блокам в наборе {self.name}")
        self.logger.debug(f"Ищем значения значения {keys}")
        self.logger.debug(f"Ищем блоки {names}")

        if names is None:
            names = self._dict_model_set.keys()

        res = {}
        for block_name in names:
            self.logger.debug(f"Обрабатываем модель {block_name}")

            if block_name not in self._dict_model_set.keys():
                self.logger.error(
                    f"Попытка считать значения из несуществующего блока в наборе {self.name} функциональный блок {block_name}")
                raise KeyError

            if keys is None:
                variables_to_read = self[block_name].parameters.as_dict().keys()
            else:
                variables_to_read = list(set(keys) & set(self[block_name].parameters.as_dict().keys()))  # Берём только те элементы, которые есть в перечне сенсоров блока
                difference = list(set(keys).difference(variables_to_read))
                if difference:
                    self.logger.warning(f"Для блока {block_name} запрошены несуществующие параметры {difference}")

            res[block_name] = self[block_name].get_state(variables_to_read)

        return res

    def compute(self,
                tick_duration:Number | dict[str, Number],
                names: list[str] | None = None,
                time_for_not_specified: Number = None) -> None:
        """
        compute
        ---
        Метод для вычисления всех или части функциональных блоков на заданное время
        Аргументы:
            tick_duration:Number | dict[str, Number]            - Время, на которое необходимо провести вычисление, может быть общим для всех или заданным индивидуально
            names: list[str] = None                             - Массив имён блоков, для которых надо провести вычисления
            time_for_not_specified: Number = None               - Время, которое надо применить к функциональным блокам, не заданным в tick_duration при задании в виде словаря
        """

        self.logger.info(f"Вычисляем функциональные блоки банка {self.name}")
        self.logger.debug(f"Время тиков {tick_duration}")
        self.logger.debug(f"Заданные блоки для вычисления {names}")
        self.logger.debug(f"Время для оставшихся блоков {time_for_not_specified}")

        if names is None:
            names = self._dict_model_set.keys()

        if isinstance(tick_duration, Number):
            self.logger.debug(f"Время тиков задано как число")
            for block_name in names:
                self[block_name].compute(tick_duration=tick_duration)

        if isinstance(tick_duration, dict):
            self.logger.debug(f"Время тиков задано как словарь")
            for block_name in names:
                if block_name not in self._dict_model_set.keys():
                    self.logger.error(f"Попытка вычислить несуществующий блок {block_name} в наборе {self.name}")
                    raise KeyError
                if block_name in tick_duration.keys():
                    self[block_name].compute(tick_duration=tick_duration[block_name])
                elif time_for_not_specified is not None:
                    self[block_name].compute(tick_duration=time_for_not_specified)
                else:
                    self.logger.error(f"Попытка вычислить функциональный блок {block_name} в наборе {self.name}, но не задан период вычисления")
                    raise ValueError(f"Не задан период вычисления функционального блока")

    def __getitem__(self, item) -> FunctionalBlock:
        return self._dict_model_set[item]


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
    logger = logging.getLogger(__name__)
    model_1 = FunctionalBlock(logger, model_params_1, name="model 1")
    model_2 = FunctionalBlock(logger, model_params_2, name="model 2")
    model_bank = FunctionalBlockBank(logger=logger, model_set=[model_1, model_2], name="test model_bank")
    print(model_bank.get_state(keys=['x2'], names=["model 1"]))
    print(model_bank.read_sensors())
    model_bank.load_variables({'x2':3, 'x1': 2})
    print(model_bank.get_state())



