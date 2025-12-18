import logging
import copy

from basics import SimulationEngine, Historizer, FunctionalBlockBank, ControlSystem, ParameterSet, ColoredFormatter
from examples import PIDController, PIDEstimator, PIDSupervisor, ARXTankModel

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

historizer = Historizer()

# Модель: выбираем среднюю рабочую точку M2, шаг дискретизации 5 c (как в статье)
tank_bank = ARXTankModel.build_tank_model_bank(logger)
plant = tank_bank["Tank_M2_mid"]

def make_controller(name: str, kp: float, ki: float, kd: float) -> PIDController.PIDController:
    params = copy.deepcopy(PIDController.pid_controller_parameters)
    params["setpoint"] = 8.0
    params["Kp"] = kp
    params["Ki"] = ki
    params["Kd"] = kd
    params["u_min"] = 0.0
    params["u_max"] = 100.0
    return PIDController.PIDController(logger=logger, parameters=params, name=name)


controller_bank = FunctionalBlockBank(
    logger=logger,
    model_set=[
        make_controller("Controller_M1", kp=1.8, ki=0.35, kd=0.10),  # мягкий
        make_controller("Controller_M2", kp=2.2, ki=0.45, kd=0.12),  # средний
        make_controller("Controller_M3", kp=2.6, ki=0.55, kd=0.15),  # жесткий
    ],
    name="Controller bank",
)

estimator_params = copy.deepcopy(PIDEstimator.pid_tank_estimator_parameters)
estimator_params["setpoint"] = 8.0
estimator_bank = FunctionalBlockBank(
    logger=logger,
    model_set=[PIDEstimator.PIDTankEstimator(logger=logger, parameters=estimator_params, name="PIDEstimator")],
    name="Estimator bank",
)

supervisor = PIDSupervisor.PIDSupervisor(
    logger=logger,
    controller_bank=controller_bank,
    estimator_bank=estimator_bank,
    name="PID supervisor",
)
control_system = ControlSystem(
    logger=logger,
    parameters=ParameterSet(),
    supervisor=supervisor,
    control_action_keys=["u"],
    name="PID control system",
)

sim = SimulationEngine(
    name="ARX Tank Simulation",
    model=plant,
    control_system=control_system,
    historizer=historizer,
    tick_duration=5.0,
    logger=logger,
)

# Запуск: 200 секунд (40 шагов по 5с)
sim.run(simulation_time=200)

# Смена уставки и возмущения
for ctrl in controller_bank.model_set:
    ctrl.parameters["setpoint"] = 12.0
estimator_bank.model_set[0].parameters["setpoint"] = 12.0
plant.parameters["disturbance"] = 0.05
sim.run(simulation_time=200)

historizer.save_history()
