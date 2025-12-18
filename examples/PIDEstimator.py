from basics import FunctionalBlock, Parameter, ParameterSet
from numbers import Number


class PIDEstimator(FunctionalBlock):
    def compute(self, tick_duration: Number = None) -> None:
        self.parameters["Controller_PID"] = 1


pid_estimator_parameters = ParameterSet(
    y=Parameter("y", 0),
    Controller_PID=Parameter("Controller_PID", 1, sensor=True),
)


class PIDTankEstimator(FunctionalBlock):
    """Heuristic, data-driven selector for three PID controllers on the tank."""

    def compute(self, tick_duration: Number = None) -> None:
        if tick_duration is None or tick_duration == 0:
            tick_duration = 1.0

        def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
            return max(lo, min(hi, val))

        setpoint = self.parameters["setpoint"].value
        y = self.parameters["y"].value
        prev_error = self.parameters["prev_error"].value

        error = setpoint - y
        derr = (error - prev_error) / tick_duration

        crossing = error * prev_error < 0 
        abs_error = abs(error)
        abs_derr = abs(derr)

        q1 = 0.7  # soft
        q2 = 0.8  # mid
        q3 = 0.7  # strong

        if crossing:
            q1 += 0.3
            q2 -= 0.1
            q3 -= 0.3
        elif error > 1.0 and derr >= 0:
            q3 += 0.3
            q2 -= 0.1
        elif error < -1.0:
            q1 += 0.2
            q3 -= 0.2

        q3 -= 0.1 * min(1.0, abs_derr / max(1e-6, abs_error + 1e-6))

        self.parameters["Controller_M1"] = clamp(q1)
        self.parameters["Controller_M2"] = clamp(q2)
        self.parameters["Controller_M3"] = clamp(q3)

        self.parameters["prev_error"] = error


pid_tank_estimator_parameters = ParameterSet(
    y=Parameter("y", 0, sensor=False),
    setpoint=Parameter("setpoint", 8.0, sensor=False),
    prev_error=Parameter("prev_error", 0.0, sensor=False),
    Controller_M1=Parameter("Controller_M1", 0.0, sensor=True),
    Controller_M2=Parameter("Controller_M2", 0.0, sensor=True),
    Controller_M3=Parameter("Controller_M3", 0.0, sensor=True),
)
