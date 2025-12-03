from basics import FunctionalBlock, Parameter, ParameterSet
from numbers import Number
import random


class Controller(FunctionalBlock):
    def compute(self, tick_duration: Number = None) -> None:
        level = self.parameters["Level"].value
        if level <= self.parameters["Level_boundary"].value:
            if self.parameters["Strength"].value > 0:
                self.parameters['Level_control'] = self.parameters['Strength'].value
            else:
                self.parameters['Level_control'] = 0
        else:
            if self.parameters["Strength"].value < 0:
                self.parameters['Level_control'] = self.parameters['Strength'].value
            else:
                self.parameters['Level_control'] = 0


controller_parameters = ParameterSet(
    # Параметр уровня, обращаться по ключу "Level", начальное значение 0, не является сенсором, так как для контроллера это входное значение
    Level=Parameter("Level", 0, min_value=0),
    # Параметр - граница включения управления, обращаться по ключу "Level_boundary", начальное значение 0
    Level_boundary=Parameter("Level boundary", 0, min_value=0),
    # Параметр управляемого изменения уровня, обращаться по ключу "Level_delta", начальное значение 0, управляющее воздействие, выходное значение контроллера => сенсор
    Level_control=Parameter("Level control", 0, sensor=True),
    # Параметр силы управления, обращаться по ключу "Strength", начальное значение 0, для настройки управляющего воздействия
    Strength=Parameter("Strength", 0)
)