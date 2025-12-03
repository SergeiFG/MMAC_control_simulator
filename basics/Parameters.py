import sympy as sp
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Union
from numbers import Number


@dataclass
class Parameter:
    """
    Parameter
    ---
    Базовый класс параметров физических моделей.
    Определяет основные взаимодействия и возможности моделей физических систем для математического моделирования.

    Аргументы:
        name: str                                           - Имя параметра, обязательно для заполнения
        value: Any                                          - Значение параметра
        sensor: bool = False                                - Является ли параметр измеряемым, если да, у системы управления есть доступ к его измерениям с погрешностью
        units: str = ""                                     - Единицы измерения параметра
        description: str = ""                               - Описание параметра
        category: str = "parameter"                         - Категории параметров, пока никак не используются
        validator: Optional[Callable[[Any], bool]] = None   - Функция с пользовательской проверкой, заменяет базовую проверку по границам, опциональна
        min_value: Optional[float] = None                   - Минимальное значение параметра, опционально
        max_value: Optional[float] = None                   - Максимальное значение параметра, опционально
        dtype: Optional[type] = None                        - Тип данных в параметре, для проверки и приведения, опционально
    """

    name: str
    value: Any
    sensor: bool = False
    units: str = "" # TODO: Добавить в отчёт по переменным
    description: str = "" # TODO: Добавить в отчёт по переменным
    category: str = "parameter"  # TODO: придумать как логику использования категорий, если нужно

    min_value: Optional[float] = None
    max_value: Optional[float] = None
    dtype: Optional[type] = None  # тип данных (float, int, bool, str, np.ndarray)

    sensor_noise: Optional[Callable[[Number], Number]] = None  # Функция для добавления шума, ограничений и нелинейности измерения параметра

    metadata: dict[str, Any] = field(default_factory=dict)  # произвольные метаданные

    def __setattr__(self, name, value):
        """
        __setattr__
        ---
        Метод для автоматического применения типа данных при изменении значения
        """
        if name == "value" and self.dtype is not None:
            value = self.dtype(value)
        super().__setattr__(name, value)

    def validate(self) -> None: # TODO: Подумать, может стоит разделить логику обрезания значения и невозможных значений
        """
        validate
        ---
        Метод проверки, входит ли параметр в свои границы, возвращает ошибку, если параметр вышел за границы
        """
        if self.value is None:
            raise ValueError(f"{self.name}: Значение не задано")
        if self.min_value is not None and self.value < self.min_value:
            raise ValueError(f"{self.name}: ниже минимума ({self.value} < {self.min_value})")
        if self.max_value is not None and self.value > self.max_value:
            raise ValueError(f"{self.name}: выше максимума ({self.value} > {self.max_value})")
        return None

    def read_sensor(self):
        """
        read_sensor
        ---
        Метод
        """
        if self.sensor_noise is None:
            return self.value
        else:
            return self.sensor_noise(self.value)

    def __str__(self):
        return f"{self.name} = {self.value} {self.units}"

    def __repr__(self):
        return f"{self.name}={self.value}"


class DerivedParameter(Parameter):
    """
    DerivedParameter(Parameter)
    ---
    Класс для зависимых параметров, выражаемых как формула от задаваемых.
    Позволяет ввести зависимости, формулу и вычислить значение зависимого параметра.
    Аргументы:
        name: str                                           - Имя параметра, обязательно для заполнения
        formula: Callable[[Any], Number]                    - Формула для вычисления зависимого параметра
        dependencies: list[str]                             - Перечень зависимостей, из которых вычисляется зависимый параметр
        units: str = ""                                     - Единицы измерения параметра
        sensor: bool = False                                - Является ли параметр измеряемым, если да, у системы управления есть доступ к его измерениям с погрешностью
        description: str = ""                               - Описание параметра
        category: str = "parameter"                         - Категории параметров, пока никак не используются
        validator: Optional[Callable[[Any], bool]] = None   - Функция с пользовательской проверкой, заменяет базовую проверку по границам, опциональна
        min_value: Optional[float] = None                   - Минимальное значение параметра, опционально
        max_value: Optional[float] = None                   - Максимальное значение параметра, опционально
        dtype: Optional[type] = None                        - Тип данных в параметре, для проверки и приведения, опционально

    Аргументы после dependencies являются необязательными и передаются полностью через **kwargs
    ! В dependencies записывать то, как переменные называются в питоне, а не значение поля name
    self._symbolic_expr                                     - Символьное выражение для вычисляемого параметра

    """
    def __init__(self, name: str, formula: Callable[[Any], Number], dependencies: list[str], **kwargs):
        """
        __init__
        ---
        Конструктор класса зависимых параметров.
        Идентичен базовому классу Parameter, дополнительные поля: formula и dependencies для создания формулы вычисления зависимых параметров.
        """
        super().__init__(name=name, value=None, **kwargs)
        self.category = "derived"
        self.formula_func = formula
        self.dependencies = dependencies
        self._symbolic_expr = None  # символьное выражение будет создано позже

    def build_symbolic(self):
        """Создаёт символьное выражение из зависимости"""
        symbols = [sp.Symbol(dep) for dep in self.dependencies]
        expr = self.formula_func(*symbols)
        try:
            self._symbolic_expr = expr
        except Exception:
            self._symbolic_expr = None
        return

    def compute(self, parameters: "ParameterSet"):
        """Численный расчёт значения"""
        values = [parameters[d].value for d in self.dependencies]
        self.value = self.formula_func(*values)
        return self.value

    def symbolic(self):
        """Возвращает символьное выражение"""
        return self._symbolic_expr


class ParameterSet:
    """
    ParameterSet
    ---
    Класс для связи и управления набором параметров

    """
    def __init__(self, **params: Parameter | DerivedParameter):
        """
        __init__
        ---
        Конструктор класса ParameterSet.
        Обеспечивает подготовку к работе с зависимыми параметрами - построение графа зависимостей, проверку на циклы,
        вычисляет начальное значение зависимых параметров и строит символьные выражения.

        Аргументы:
            **params: Parameter     - Набор именованных параметров (класс Parameter или DerivedParameter)
        """
        self._params = params

        self._build_dependency_graph()
        self._check_for_cycles()
        self.order = self._topological_sort()
        self.update_derived()
        self._build_symbolic_expressions() # TODO: понять, нужно ли, может ломать некоторые функции

        # Перенесено в self.update_derived()
        # for key in self._params: # При вводе значений проверим, что все числа корректные
        #     self._params[key].validate()

    def _build_dependency_graph(self) -> None:
        """
        _build_dependency_graph
        ---
        Метод построения графа зависимостей между параметрами.
        Необходим для решения проблемы многоуровневой зависимости, когда один зависимый параметр вычисляется из другого зависимого параметра.
        """
        self._graph = {k: [] for k in self._params}
        for name, p in self._params.items():
            if isinstance(p, DerivedParameter):
                for dep in p.dependencies:
                    if dep not in self._params:
                        raise KeyError(f"Зависимость '{dep}' не найдена для '{name}'")
                    self._graph[dep].append(name)

    def _check_for_cycles(self) -> None:
        """
        _build_dependency_graph
        ---
        Метод проверки графа на наличие циклов (DFS).
        Необходим для решения проблемы многоуровневой зависимости, когда один зависимый параметр вычисляется из другого зависимого параметра.
        """
        visited, stack = set(), set()

        def dfs(node):
            if node not in self._graph:
                return False
            if node in stack:
                raise ValueError(f"Обнаружена циклическая зависимость, начиная с '{node}'")
            if node in visited:
                return False
            stack.add(node)
            for neighbor in self._graph[node]:
                dfs(neighbor)
            stack.remove(node)
            visited.add(node)

        for node in self._graph:
            dfs(node)

    def _topological_sort(self) -> list[str]:
        """Порядок пересчёта параметров"""
        from collections import deque
        indegree = {k: 0 for k in self._params}
        for p in self._params.values():
            if isinstance(p, DerivedParameter):
                for d in p.dependencies:
                    indegree[p.name] += 1
        q = deque([k for k, v in indegree.items() if v == 0])
        order = []
        while q:
            n = q.popleft()
            order.append(n)
            for m in self._graph.get(n, []):
                indegree[m] -= 1
                if indegree[m] == 0:
                    q.append(m)
        return order

    def update_derived(self) -> None:
        """
        update_derived
        ---
        Метод для пересчёта всех зависимых параметров.
        Также содержит проверку всех параметров на соблюдение границ.
        Запускать вручную на каждой итерации!"""
        # order = self._topological_sort() # Будем считать, что формулы не меняются, поэтому пересчитывать граф вычислений нет нужды
        for name in self.order:
            p = self._params[name]
            if isinstance(p, DerivedParameter):
                p.compute(self)

        for key in self._params: # При обновлении значений проверим, что все числа корректные
            self._params[key].validate()

    def _build_symbolic_expressions(self) -> None:
        """Построить символьные выражения для DerivedParameter"""
        for name in self._topological_sort():
            p = self._params[name]
            if isinstance(p, DerivedParameter):
                p.build_symbolic()

    def __getitem__(self, key) -> Parameter:
        return self._params[key]

    def __setitem__(self, key, value) -> None:
        """Проверка данных при изменении любого из параметов"""
        if key not in self._params:
            raise KeyError(f"{key} не найден.")
        p = self._params[key]
        if isinstance(p, DerivedParameter):
            raise AttributeError(f"{key} — вычисляемый параметр.")
        p.value = value
        p.validate()
        # Убрал автоматическое обновление, чтобы постоянно не пересчитывать, пока все параметры не заданы
        # self.update_derived()

    def as_dict(self, keys: list[str] = None, read_sensors: bool = False) -> dict[str, Number]:
        """
        as_dict
        ---
        Метод выгрузки всех или части значений в виде словаря dict[str, Number]

        Аргументы:
            keys: list[str] = None      - Массив ключей при необходимости ограничивает выгружаемые параметры
            read_sensors: bool = False  - Нужно ли применять шум сенсоров при считывании данных
        """
        if read_sensors: # Если нужно считывать данные с сенсоров, то берём в учёт шум сенсоров
            if keys is None:
                return {k: p.read_sensor() for k, p in self._params.items()}
            else:
                return {key: self._params[key].read_sensor() for key in keys}
        else: # Если нужно взять просто значение, то берём напрямую value
            if keys is None:
                return {k: p.value for k, p in self._params.items()}
            else:
                return {key: self._params[key].value for key in keys}

    def load_dict(self, data: dict[str, Number]) -> None:
        """
        load_dict
        ---
        Метод загрузки всех или части значений в виде словаря dict[str, Number]

        Аргументы:
            d: dict[str, Number]      - Словарь с необходимыми именами и значениями для записи
        """
        for key, value in data.items():
            if key not in self._params:
                raise KeyError(f'Попытка записать несуществующий {key}')
            self[key] = value

    def __repr__(self):
        return ", ".join(f"{k}={p.value}" for k, p in self._params.items() if p.value is not None)


if __name__ == '__main__':
    class Model:
        def __init__(self):
            self.parameters = ParameterSet(
                x1 = Parameter("x1", 4, sensor=True, max_value=5),
                x2 = Parameter("x2", 5, sensor=True),
                y1 = DerivedParameter("y1", lambda x1, x2: x1**2+x2, ["x1","x2"], units='m2'),
                y2=DerivedParameter("y2", lambda x: x*2, ["y3"]),
                y3 = DerivedParameter("y3", lambda x: x * 2, ["y1"], sensor=True, sensor_noise=lambda x:x+1)
                )


    model = Model()
    # print(model.parameters)
    # model.parameters["y1"] = 2
    print(model.parameters.as_dict(['x2', 'y1']))
    print(model.parameters.as_dict())

    a = {'x1': 2, 'x2': 3}

    model.parameters.load_dict(a)
    model.parameters.update_derived()
    print(model.parameters)
    print(model.parameters.as_dict(['y3'], read_sensors=True))

    print(model.parameters.as_dict().keys())

    b = model.parameters['x1']
    print(b)
