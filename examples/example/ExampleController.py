from basics import FunctionalBlock, Parameter, ParameterSet
from numbers import Number
import random


class Controller(FunctionalBlock):
    def compute(self, tick_duration: Number = None) -> None:
        # Управляющиее воздействие от контроллера вычисляется как сила*текущий уровень
        self.parameters['Level_control'] = self.parameters['Strength'] * self.parameters["Level"]


controller_parameters = ParameterSet(
    # Параметр уровня, обращаться по ключу "Level", начальное значение 0, не является сенсором, так как для контроллера это входное значение
    Level=Parameter("Level", 0),
    # Параметр силы управления, обращаться по ключу "Strength", начальное значение 0, для настройки управляющего воздействия
    Strength=Parameter("Strength", 0.75),
    # управляющее воздействие данного контроллера, так как выходное значение отмечаем сенсор
    Level_control=Parameter("Level control", 0, sensor=True),
)