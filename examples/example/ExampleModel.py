from basics import FunctionalBlock, Parameter, ParameterSet
from numbers import Number
import random
from scipy.integrate import solve_ivp


class ExampleModel(FunctionalBlock):
    @staticmethod
    def update_level(t, y, omega, control):
        """Функция, описывающая динамику системы. Представлена в виде системы диф уравнений в нормальной форме
        в данном случае это диф уравнение y`` = -omega**2 * y, которое решается как гармонические колебания
        В нормальной форме это y`= y1, y1` = -omega**2 * y
        Дополнительно добавим учёт внешнего управления"""
        level, level_dot = y
        return [level_dot, -1*omega**2*level + control]

    def compute(self, tick_duration:Number = None) -> None:
        self.logger.debug(f"Уровень в модели до обновления {self.parameters['Level']}")
        # Посчитаем новые значения уровня и его скорости как решение ОДУ
        sol = solve_ivp(fun=self.update_level,
                        y0=[self.parameters['Level'], self.parameters['Level_dot']],
                        method="RK45",
                        t_span=(0, tick_duration),
                        t_eval=[0, tick_duration],
                        args=(self.parameters["omega"], self.parameters["Level_control"]))
        if not sol.success:
            self.logger.error(f"Не удалось решить ОДУ динамики модели {str(self.parameters)} ")

        # Записываем результаты вычисления
        self.parameters['Level_dot'] = sol.y[1, -1]
        self.parameters['Level'] = sol.y[0, -1]

        self.logger.debug(f"Уровень в модели после обновления {self.parameters['Level']}")


model_parameters = ParameterSet(
                # Параметр уровня, обращаться по ключу "Level", начальное значение 0, минимальное значение -10, максимальное - +10, является сенсором, учитывает шум
                Level = Parameter("Level", 8, sensor=True, sensor_noise=lambda x: x+random.uniform(-1, 1)),
                # Параметр скорости изменения уровня, обращаться по ключу "Level_dot", начальное значение 0
                Level_dot = Parameter("Level speed", 0),
                # Параметр внешнего управления, влияет на вторую производную, обращаться по ключу "Level_control", начальное значение 0
                Level_control = Parameter("Level control", 0),
                # Параметр управляемого изменения уровня, влияет на скорость изменения уровня, обращаться по ключу "Level_control", начальное значение 0
                omega = Parameter("omega", 1)
                )
# , min_value=-15, max_value=15