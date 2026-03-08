from basics import SimulationEngine, Historizer, FunctionalBlockBank, ControlSystem, ParameterSet
from modules.supervisors import OneEstimatorSupervisor
import logging
from basics import ColoredFormatter
import copy

from examples.example import ExampleModel, ExampleController, ExampleSupervisor, ExampleEstimator

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
model_parameters["Level"] = 5
model_parameters["Level_dot"] = 0
model = ExampleModel.ExampleModel(logger=logger, parameters=model_parameters, name="Example level control model")

# Настроить контроллеры, создать банк контроллеров
min_controller_parameters = copy.deepcopy(ExampleController.controller_parameters)
min_controller_parameters["Strength"] = 0.8
min_controller = ExampleController.Controller(logger=logger, parameters=min_controller_parameters, name="Controller_min")

max_controller_parameters = copy.deepcopy(ExampleController.controller_parameters)
max_controller_parameters["Strength"] = 0.75
max_controller = ExampleController.Controller(logger=logger, parameters=max_controller_parameters, name="Controller_max")

middle_controller_parameters = copy.deepcopy(ExampleController.controller_parameters)
middle_controller_parameters["Strength"] = 0
middle_controller = ExampleController.Controller(logger=logger, parameters=middle_controller_parameters, name="Controller_middle")

# Инициализировать эстиматор
estimator = ExampleEstimator.get_estimator(logger, boundary=4)

# Инициализировать систему управления
supervisor = OneEstimatorSupervisor(logger=logger, controllers=[min_controller, max_controller, middle_controller], estimators=[estimator], name="Example supervisor")

control_system = ControlSystem(logger=logger, parameters=ParameterSet(), supervisor=supervisor, control_action_keys=["Level_control"], name="Example Control system")

# Создание симуляции
Simulation = SimulationEngine(
    name='Example Simulation',
    model=model,
    control_system=control_system,
    historizer=historizer,
    tick_duration=0.1,
    logger=logger,
    logs_subfolder=None,
    results_subfolder='/ExampleV2'
)

# Запускаем симуляцию
Simulation.run(simulation_time=50)

historizer.save_history()

