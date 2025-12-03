from basics import SimulationEngine, Historizer, FunctionalBlockBank, ControlSystem, ParameterSet
import logging
from basics import ColoredFormatter
import copy

from examples import ExampleController, ExampleEstimator, ExampleSupervisor, ExampleModel

logger = logging.getLogger(__name__)

# Настраиваем цветной вывод в консоль, по эеланию можно убрать/заменить
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))

# уровень сообщения для вывода в консоль, рекомендуется ставить DEBUG или INFO
console_handler.setLevel(logging.DEBUG)

# Закомментировать строку, если не нужно вообще выводить в консоль
logger.addHandler(console_handler)

# Создать объект для записи истории
historizer = Historizer()

# Настроить модель
model_parameters = ExampleModel.model_parameters
model_parameters["Level"] = 1
model_parameters["Level_delta"] = 2
model = ExampleModel.ExampleModel(logger=logger, parameters=model_parameters, name="Example level control model")

# Настроить контроллеры, создать банк контроллеров
min_controller_parameters = copy.deepcopy(ExampleController.controller_parameters)
min_controller_parameters["Level_boundary"] = 3
min_controller_parameters["Strength"] = 4
min_controller = ExampleController.Controller(logger=logger, parameters=min_controller_parameters, name="Controller_min")

max_controller_parameters = copy.deepcopy(ExampleController.controller_parameters)
max_controller_parameters["Level_boundary"] = 10
max_controller_parameters["Strength"] = -4
max_controller = ExampleController.Controller(logger=logger, parameters=max_controller_parameters, name="Controller_max")

controller_bank = FunctionalBlockBank(logger=logger, model_set=[min_controller, max_controller], name="Controller bank")

# Инициализировать эстиматор
estimator_parameters = ExampleEstimator.estimator_parameters
estimator_parameters["Controller_boundary"] = 5
estimator = ExampleEstimator.Estimator(logger=logger, parameters=estimator_parameters, name="Estimator")

estimator_bank = FunctionalBlockBank(logger=logger, model_set=[estimator], name="Estimator bank")

# Инициализировать систему управления
supervisor = ExampleSupervisor.ExampleSupervisor(logger=logger, controller_bank=controller_bank, estimator_bank=estimator_bank, name="Example supervisor")

control_system = ControlSystem(logger=logger, parameters=ParameterSet(), supervisor=supervisor, control_action_keys=["Level_control"], name="Example Control system")

# Создание симуляции
Simulation = SimulationEngine(
    name='Example Simulation',
    model=model,
    control_system=control_system,
    historizer=historizer,
    tick_duration=1,
    logger=logger
)

# Запускаем симуляцию
Simulation.run(simulation_time=10)
model_parameters["Level_delta"] = -2
# Меняем параметры модели и продолжаем симуляцию
Simulation.run(simulation_time=10)

historizer.save_history()

