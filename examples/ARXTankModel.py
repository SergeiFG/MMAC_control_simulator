import logging
from numbers import Number

from basics import FunctionalBlock, Parameter, ParameterSet, FunctionalBlockBank


class ARXTankModel(FunctionalBlock):
    """
    Дискретная ARX-модель бака с уровнем жидкости (вход-выходная форма):
        y(k) = -a1*y(k-1) - a2*y(k-2) + b1*u(k-1) + b2*u(k-2) + d
    Состояние хранится как прошлые значения y,u. Выходом является уровень y.
    """

    def compute(self, tick_duration: Number = None) -> None:
        y1 = self.parameters["y_1"].value
        y2 = self.parameters["y_2"].value
        u1 = self.parameters["u_1"].value
        u2 = self.parameters["u_2"].value

        a1 = self.parameters["a1"].value
        a2 = self.parameters["a2"].value
        b1 = self.parameters["b1"].value
        b2 = self.parameters["b2"].value
        d = self.parameters["disturbance"].value

        y_new = -a1 * y1 - a2 * y2 + b1 * u1 + b2 * u2 + d

        self.parameters["y"] = y_new
        self.parameters["y_2"] = y1
        self.parameters["y_1"] = y_new

        self.parameters["u_2"] = u1
        self.parameters["u_1"] = self.parameters["u"].value


def make_paramset(a1: float, a2: float, b1: float, b2: float, name: str = "") -> ParameterSet:
    return ParameterSet(
        y=Parameter("y", 0.0, sensor=True),
        y_1=Parameter("y_1", 0.0),
        y_2=Parameter("y_2", 0.0),
        u=Parameter("u", 0.0),
        u_1=Parameter("u_1", 0.0),
        u_2=Parameter("u_2", 0.0),
        a1=Parameter("a1", a1),
        a2=Parameter("a2", a2),
        b1=Parameter("b1", b1),
        b2=Parameter("b2", b2),
        disturbance=Parameter("disturbance", 0.0),
    )


def build_tank_model_bank(logger: logging.Logger) -> FunctionalBlockBank:
    models = [
        ARXTankModel(logger, make_paramset(-0.94374, -0.02457, 0.0086856, 0.000341), name="Tank_M1_high"),
        ARXTankModel(logger, make_paramset(-0.95172, -0.02322, 0.0076444, 0.000341), name="Tank_M2_mid"),
        ARXTankModel(logger, make_paramset(-0.95502, -0.02238, 0.007144, 0.00074), name="Tank_M3_low"),
    ]
    return FunctionalBlockBank(logger=logger, model_set=models, name="Tank models")
