from basics import FunctionalBlock, Parameter, ParameterSet
from numbers import Number
import random


class ExampleModel(FunctionalBlock):
    def compute(self, tick_duration:Number = None) -> None:
        self.logger.debug(f"Уровень в модели до обновления {self.parameters['Level']}")
        self.parameters['Level'] = self.parameters['Level'].value + self.parameters['Level_control'].value
        self.parameters['Level'] = self.parameters['Level'].value + self.parameters['Level_delta'].value
        self.logger.debug(f"Уровень в модели после обновления {self.parameters['Level']}")


model_parameters = ParameterSet(
                # Параметр уровня, обращаться по ключу "Level", начальное значение 0, минимальное значение 0, является сенсором, учитывает шум
                Level = Parameter("Level", 0, sensor=True, min_value=0, sensor_noise=lambda x: x+random.randint(-1, 1)),
                # Параметр естественного изменения уровня, обращаться по ключу "Level_delta", начальное значение 0
                Level_delta = Parameter("Level delta", 0),
                # Параметр управляемого изменения уровня, обращаться по ключу "Level_control", начальное значение 0
                Level_control = Parameter("Level control", 0),
                )