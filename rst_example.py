import logging
import copy

from basics import SimulationEngine, Historizer, FunctionalBlockBank, ControlSystem, ParameterSet, ColoredFormatter
from examples import ARXTankModel, RSTController, RSTEstimator, RSTSupervisor

logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

historizer = Historizer()

tank_bank = ARXTankModel.build_tank_model_bank(logger)
plant = tank_bank["Tank_M2_mid"]


def make_controller(name: str, R0: float, R1: float, T0: float, T1: float, T2: float) -> RSTController.RSTController:
    params = copy.deepcopy(RSTController.rst_controller_parameters)
    params["setpoint"] = 8.0
    params["R0"] = R0
    params["R1"] = R1
    params["R2"] = 0.0
    params["S0"] = 1.0
    params["S1"] = -1.0
    params["S2"] = 0.0
    params["T0"] = T0
    params["T1"] = T1
    params["T2"] = T2
    params["u_min"] = 0
    params["u_max"] = 100
    return RSTController.RSTController(logger=logger, parameters=params, name=name)


controller_bank = FunctionalBlockBank(
    logger=logger,
    model_set=[
        make_controller("Controller_M1", R0=61.824, R1=-46.906, T0=113.378, T1=-158.394, T2=59.933),
        make_controller("Controller_M2", R0=65.435, R1=-49.171, T0=123.609, T1=-172.686, T2=65.341),
        make_controller("Controller_M3", R0=65.592, R1=-49.235, T0=126.582, T1=-176.840, T2=66.912),
    ],
    name="Controller bank",
)

estimator_params = copy.deepcopy(RSTEstimator.rst_estimator_parameters)
estimator_bank = FunctionalBlockBank(
    logger=logger,
    model_set=[RSTEstimator.RSTEstimator(logger=logger, parameters=estimator_params, name="RSTEstimator")],
    name="Estimator bank",
)

supervisor = RSTSupervisor.RSTSupervisor(
    logger=logger,
    controller_bank=controller_bank,
    estimator_bank=estimator_bank,
    name="RST supervisor",
)
control_system = ControlSystem(
    logger=logger,
    parameters=ParameterSet(),
    supervisor=supervisor,
    control_action_keys=["u"],
    name="RST control system",
)

sim = SimulationEngine(
    name="ARX Tank Simulation RST",
    model=plant,
    control_system=control_system,
    historizer=historizer,
    tick_duration=5.0,
    logger=logger,
)


sim.run(simulation_time=300)

for ctrl in controller_bank.model_set:
    ctrl.parameters["setpoint"] = 12.0
plant.parameters["disturbance"] = 0.0
sim.run(simulation_time=300)

historizer.save_history()
