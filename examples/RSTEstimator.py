from basics import FunctionalBlock, Parameter, ParameterSet
from numbers import Number


class RSTEstimator(FunctionalBlock):
    def compute(self, tick_duration: Number = None) -> None:
        self.parameters["Controller_M2"] = 1.0
        self.parameters["Controller_M1"] = 0.8
        self.parameters["Controller_M3"] = 0.6


rst_estimator_parameters = ParameterSet(
    y=Parameter("y", 0, sensor=False),
    Controller_M1=Parameter("Controller_M1", 0.0, sensor=True),
    Controller_M2=Parameter("Controller_M2", 0.0, sensor=True),
    Controller_M3=Parameter("Controller_M3", 0.0, sensor=True),
)
