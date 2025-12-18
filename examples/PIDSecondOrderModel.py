from basics import FunctionalBlock, Parameter, ParameterSet
from numbers import Number


class PIDSecondOrderPlantModel(FunctionalBlock):
    """
    Украл в интернете модель второго порядка с вязким демпфированием, жесткостью и сухим трением.

    
    Second-order plant with viscous damping, stiffness and dry friction.
    y: position, v: velocity, u: control input.
    Equation:
        dy/dt = v
        dv/dt = (gain * u - damping * v - stiffness * y - friction * sign(v) + disturbance) / mass
    """

    def compute(self, tick_duration: Number = None) -> None:

        y = self.parameters["y"].value
        v = self.parameters["v"].value
        u = self.parameters["u"].value

        mass = self.parameters["mass"].value
        damping = self.parameters["damping"].value
        stiffness = self.parameters["stiffness"].value
        gain = self.parameters["gain"].value
        friction = self.parameters["friction"].value
        disturbance = self.parameters["disturbance"].value

        sign_v = 1 if v > 0 else -1 if v < 0 else 0
        acceleration = (gain * u - damping * v - stiffness * y - friction * sign_v + disturbance) / mass

        y_new = y + tick_duration * v
        v_new = v + tick_duration * acceleration

        y_min = self.parameters["y"].min_value
        if y_min is not None:
            y_new = max(y_min, y_new)

        self.parameters["y"] = y_new
        self.parameters["v"] = v_new


pid_second_order_parameters = ParameterSet(
    y=Parameter("y", 0.0, sensor=True, min_value=0.0),
    v=Parameter("v", 0.0, sensor=True),
    u=Parameter("u", 0.0),
    mass=Parameter("mass", 1.0, min_value=0.01),
    damping=Parameter("damping", 0.6, min_value=0.0),
    stiffness=Parameter("stiffness", 0.3, min_value=0.0),
    gain=Parameter("gain", 1.0, min_value=0.0),
    friction=Parameter("friction", 0.2, min_value=0.0),
    disturbance=Parameter("disturbance", 0.0),
)
