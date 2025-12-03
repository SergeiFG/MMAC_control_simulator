import logging

from basics import Parameter, DerivedParameter, ParameterSet
from numbers import Number


class FunctionalBlock:
    """
    BaseModel
    ---
    Базовый класс физических моделей.
    Определяет основные взаимодействия и возможности моделей физических систем для математического моделирования.

    """

    def __init__(self, logger: logging.Logger, parameters: ParameterSet, name: str = "", *args, **kwargs): #TODO: добавить больше логирования
        """
        __init__
        ---
        Аргументы:
            logger                          - Логгер для записи логов в файл и консоль
            parameters: ParameterSet        - Набор параметров данной модели

        Поля:
            self.variables                  - Массив имён переменных, которые доступны для записи = входные переменные
            self.sensors                    - Массив имён переменных, которые доступны для чтения = выходные переменные
        """
        self.logger = logger
        self.logger.info(f"Инициализация функционального блока {name} с параметрами {parameters}")

        self.parameters = parameters
        if name == "":
            self.logger.warning(f"Не задано имя функционального блока")
        self.name = name

        self.variables = []
        self.sensors = []

        for key in self.parameters.as_dict().keys():
            if not isinstance(self.parameters[key], DerivedParameter):
                self.variables.append(key)
            if self.parameters[key].sensor is True:
                self.sensors.append(key)

        self.logger.debug(f"Сенсоры функционального блока {self.name}: {self.sensors}")
        self.logger.debug(f"Переменные функционального блока {self.name}: {self.variables}")

    def compute(self, tick_duration:Number = None) -> None:
        """
        update
        ---

        Метод, в котором необходимо реализовать логику физической модели.
        TODO: Подумать над методом численного дифференцирования / интегрирования

        Аргументы:
            tick_duration:Number = None         - Время математического моделирования функции данного блока
        """

        self.logger.error("Метод update не определён")
        raise NotImplementedError('Метод update не определён')

    def read_sensors(self,  keys: list[str] = None) -> dict[str, Number]:
        """
        read_sensors
        ---
        Метод выгрузки всех или части значений в виде словаря dict[str, Number]
        Используется для считывания сенсоров.
        Аргументы:
            keys: list[str] = None      - Массив ключей при необходимости ограничивает выгружаемые параметры
        """

        self.logger.info(f'Начат сбор данных сенсоров физической модели')
        self.logger.debug(f'Для сбора данных сенсоров использованы заданы ключи: {keys}')

        if keys is not None:
            keys = list(set(keys) & set(self.sensors))
        else:
            keys = self.sensors

        self.logger.debug(f'Итоговый набор ключей для сбора данных сенсоров: {keys}')
        res = self.parameters.as_dict(keys=keys, read_sensors=True)
        self.logger.debug(f'Собраны данные сенсоров системы: {res}')

        return res

    def get_state(self,  keys: list[str] = None) -> dict[str, Number | str]:
        """
        get_state
        ---
        Метод выгрузки всех или части значений в виде словаря dict[str, Number]
        Используется для считывания состояния модели для архива.
        Аргументы:
            keys: list[str] = None      - Массив ключей при необходимости ограничивает выгружаемые параметры
        """

        self.logger.info(f'Начат сбор состояния физической модели')
        self.logger.debug(f'Для сбора состояния использованы заданы ключи: {keys}')

        if keys is not None:
            keys = list(set(keys) & set(self.parameters.as_dict().keys()))
        else:
            keys = self.parameters.as_dict().keys()

        self.logger.debug(f'Итоговый набор ключей для сбора состояния: {keys}')
        res = self.parameters.as_dict(keys=keys, read_sensors=False)
        self.logger.debug(f'Собрано состояние системы: {res}')
        return res

    def load_variables(self, data: dict[str, Number]) -> None:
        """
        load_varibles
        ---
        Метод загрузки всех или части значений в виде словаря dict[str, Number]

        Аргументы:
            d: dict[str, Number]      - Словарь с переменными и их значениями для загрузки
        """
        self.logger.info(f'Начато обновление параметров функционального блока {self.name}')
        self.logger.debug(f'Для обновления использованы значения {data}')
        self.parameters.load_dict(data)
        self.parameters.update_derived()
        self.logger.info(f'Обновлены значения параметров физической модели')
        self.logger.debug(f'Новые параметры физической модели {self.parameters}')


if __name__ == '__main__':

    def test_func(x, y):
        return min(x,0)*5 + max(y,15)

    model_params = ParameterSet(
                    x1 = Parameter("x1", 4, sensor=True, max_value=5),
                    x2 = Parameter("x2", 5, sensor=True),
                    y1 = DerivedParameter("y1", lambda x1, x2: x1**2+x2, ["x1","x2"], units='m2'),
                    y2=DerivedParameter("y2", lambda x: x*2, ["y3"]),
                    y3 = DerivedParameter("y3", lambda x: x * 2, ["y1"], sensor=True, sensor_noise=lambda x:x+1)
                    )
    logger = logging.getLogger(__name__)
    model = FunctionalBlock(logger, model_params)
    print(model.get_state())
    print(model.read_sensors())

    model.load_variables({'x2': 8})
    print(model.get_state())
