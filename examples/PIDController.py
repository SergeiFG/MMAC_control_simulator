from basics import FunctionalBlock, Parameter, ParameterSet
from numbers import Number


class PIDController(FunctionalBlock):
    def compute(self, tick_duration: Number = None) -> None:
        if tick_duration is None:
            raise ValueError("tick_duration is required for PIDController.compute")

        error = self.parameters["setpoint"].value - self.parameters["y"].value
        integral = self.parameters["integral"].value + error * tick_duration
        prev_error = self.parameters["prev_error"].value
        derivative = (error - prev_error) / tick_duration if tick_duration != 0 else 0

        u = (
            self.parameters["Kp"].value * error
            + self.parameters["Ki"].value * integral
            + self.parameters["Kd"].value * derivative
        )

        u_min = self.parameters["u_min"].value
        u_max = self.parameters["u_max"].value
        u = max(u_min, min(u, u_max))

        self.parameters["integral"] = integral
        self.parameters["prev_error"] = error
        self.parameters["u"] = u


pid_controller_parameters = ParameterSet(
    y=Parameter("y", 0),
    setpoint=Parameter("setpoint", 10),
    Kp=Parameter("Kp", 1.0),
    Ki=Parameter("Ki", 0.0),
    Kd=Parameter("Kd", 0.0),
    integral=Parameter("integral", 0.0),
    prev_error=Parameter("prev_error", 0.0),
    u=Parameter("u", 0.0, sensor=True),
    u_min=Parameter("u_min", -10.0),
    u_max=Parameter("u_max", 10.0),
)
