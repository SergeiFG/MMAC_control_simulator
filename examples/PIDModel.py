from basics import FunctionalBlock, Parameter, ParameterSet
from numbers import Number


class PIDPlantModel(FunctionalBlock):
    def compute(self, tick_duration: Number = None) -> None:

        y = self.parameters["y"].value
        u = self.parameters["u"].value
        gain = self.parameters["gain"].value
        tau = self.parameters["tau"].value
        disturbance = self.parameters["disturbance"].value

        dydt = (gain * u - y) / tau + disturbance
        y_new = y + tick_duration * dydt
        self.parameters["y"] = max(self.parameters["y"].min_value or -float("inf"), y_new)


pid_model_parameters = ParameterSet(
    y=Parameter("y", 0.0, sensor=True, min_value=0.0),
    u=Parameter("u", 0.0),
    gain=Parameter("gain", 1.0, min_value=0.0),
    tau=Parameter("tau", 1.0, min_value=0.01),
    disturbance=Parameter("disturbance", 0.0),
)
