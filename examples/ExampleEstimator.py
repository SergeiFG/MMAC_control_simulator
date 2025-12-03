from basics import FunctionalBlock, Parameter, ParameterSet
from numbers import Number
import random


class Estimator(FunctionalBlock):
    # В зависимости от значения уровня выдать контроллерам свои показатели качества
    def compute(self, tick_duration: Number = None) -> None:
        level = self.parameters["Level"].value
        if level <= self.parameters["Controller_boundary"].value:
            self.parameters['Controller_min'] = 1
            self.parameters['Controller_max'] = 0
        else:
            self.parameters['Controller_min'] = 0
            self.parameters['Controller_max'] = 1


estimator_parameters = ParameterSet(
    # Параметр уровня, обращаться по ключу "Level", начальное значение 0, не является сенсором, так как для контроллера это входное значение
    Level=Parameter("Level", 0, min_value=0),
    # Параметр границы переключения между контроллерами, обращаться по ключу "Controller_boundary", начальное значение 0
    Controller_boundary=Parameter("Controller boundary", 5),
    # Параметр качества контроллера с именем Controller_min, обращаться по ключу "Controller_min", начальное значение 0, выходное значение эстиматора => сенсор
    Controller_min=Parameter("Controller min", 0, sensor=True),
    # Параметр качества контроллера с именем Controller_max, обращаться по ключу "Controller_max", начальное значение 0, выходное значение эстиматора => сенсор
    Controller_max=Parameter("Controller max", 0, sensor=True)
)