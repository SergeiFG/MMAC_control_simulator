import logging
import copy

from basics import SimulationEngine, Historizer, FunctionalBlockBank, ControlSystem, ParameterSet, ColoredFormatter
from examples import PIDController, PIDEstimator, PIDSupervisor, PIDSecondOrderModel

logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

historizer = Historizer()

model_params = copy.deepcopy(PIDSecondOrderModel.pid_second_order_parameters)
model_params["y"] = 0.0
model_params["v"] = 0.0
model_params["disturbance"] = 0.0
model = PIDSecondOrderModel.PIDSecondOrderPlantModel(logger=logger, parameters=model_params, name="Second-order plant")

controller_params = copy.deepcopy(PIDController.pid_controller_parameters)
controller_params["setpoint"] = 5.0
controller_params["Kp"] = 3.0
controller_params["Ki"] = 0.8
controller_params["Kd"] = 0.3
controller_bank = FunctionalBlockBank(
    logger=logger,
    model_set=[PIDController.PIDController(logger=logger, parameters=controller_params, name="Controller_PID")],
    name="Controller bank",
)

estimator_params = copy.deepcopy(PIDEstimator.pid_estimator_parameters)
estimator_bank = FunctionalBlockBank(
    logger=logger,
    model_set=[PIDEstimator.PIDEstimator(logger=logger, parameters=estimator_params, name="PIDEstimator")],
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

# Движок симуляции
sim = SimulationEngine(
    name="PID Simulation",
    model=model,
    control_system=control_system,
    historizer=historizer,
    tick_duration=0.1,
    logger=logger,
)

# Запуск
sim.run(simulation_time=10)

# Изменяем уставку и вводим возмущение
controller_params["setpoint"] = 8.0
model_params["disturbance"] = 0.5
sim.run(simulation_time=10)

# Вывод итоговых значений
model_state = historizer.records.get("model_state")
control_actions = historizer.records.get("control_actions")
if model_state is not None and control_actions is not None:
    last_y = model_state.iloc[-1]["y"]
    last_v = model_state.iloc[-1]["v"]
    last_u = control_actions.iloc[-1]["u"]
    logger.info(f"Итоговое состояние: y={last_y:.3f}, v={last_v:.3f}, u={last_u:.3f}")

historizer.save_history()
