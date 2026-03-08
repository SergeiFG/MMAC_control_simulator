from basics import FunctionalBlock, Parameter, ParameterSet
from numbers import Number


class RSTController(FunctionalBlock):
    def compute(self, tick_duration: Number = None) -> None:
        y = self.parameters["y"].value
        y_1 = self.parameters["y_1"].value
        y_2 = self.parameters["y_2"].value

        sp = self.parameters["setpoint"].value
        sp_1 = self.parameters["sp_1"].value
        sp_2 = self.parameters["sp_2"].value

        u_1 = self.parameters["u_1"].value
        u_2 = self.parameters["u_2"].value

        R0 = self.parameters["R0"].value
        R1 = self.parameters["R1"].value
        R2 = self.parameters["R2"].value

        S0 = self.parameters["S0"].value
        S1 = self.parameters["S1"].value
        S2 = self.parameters["S2"].value

        T0 = self.parameters["T0"].value
        T1 = self.parameters["T1"].value
        T2 = self.parameters["T2"].value

        numerator = (
            T0 * sp
            + T1 * sp_1
            + T2 * sp_2
            - R0 * y
            - R1 * y_1
            - R2 * y_2
            - S1 * u_1
            - S2 * u_2
        )

        u_raw = numerator / S0

        u_min = self.parameters["u_min"].value
        u_max = self.parameters["u_max"].value
        u = max(u_min, min(u_max, u_raw))

        self.parameters["u_2"] = u_1
        self.parameters["u_1"] = u
        self.parameters["y_2"] = y_1
        self.parameters["y_1"] = y
        self.parameters["sp_2"] = sp_1
        self.parameters["sp_1"] = sp

        self.parameters["u"] = u


rst_controller_parameters = ParameterSet(
    y=Parameter("y", 0.0, sensor=True),
    y_1=Parameter("y_1", 0.0),
    y_2=Parameter("y_2", 0.0),
    setpoint=Parameter("setpoint", 8.0),
    sp_1=Parameter("sp_1", 8.0),
    sp_2=Parameter("sp_2", 8.0),
    u=Parameter("u", 0.0, sensor=True),
    u_1=Parameter("u_1", 0.0),
    u_2=Parameter("u_2", 0.0),
    R0=Parameter("R0", 1.0),
    R1=Parameter("R1", -0.5),
    R2=Parameter("R2", 0.0),
    S0=Parameter("S0", 1.0),
    S1=Parameter("S1", -1.0),
    S2=Parameter("S2", 0.0),
    T0=Parameter("T0", 1.0),
    T1=Parameter("T1", 0.0),
    T2=Parameter("T2", 0.0),
    u_min=Parameter("u_min", -1e9),
    u_max=Parameter("u_max", 1e9),
)
