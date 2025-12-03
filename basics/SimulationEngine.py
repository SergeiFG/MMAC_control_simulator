import logging, os
import warnings

from basics import FunctionalBlock, ControlSystem, Historizer
from datetime import datetime


class SimulationEngine:
    """
    SimulationEngine
    ---
    Центральный оператор имитационного моделирования.
    Отвечает за управление симуляцией, инициализацию объектов и передачу данных

    """

    def __init__(self,
                 name: str = 'Test',
                 model: FunctionalBlock = None,
                 control_system: ControlSystem = None,
                 historizer: Historizer = None,
                 tick_duration: float = 0.1,
                 logger: logging.Logger | None = None,
                 *args,
                 **kwargs
                 ) -> None:

        """
        __init__
        ---
        Аргументы:
            name: str = 'Test'                      - Имя симуляции (для сохранения логов и картинок)
            model : object = None                   - Система имитационного моделирования, содержит математическую модель и сенсоры
            control_system: object = None           - Система управления, формирует управляющие воздействия
            historizer: object = None               - Хранилище данных
            tick_duration: float = 0.1              - Время одного шага симуляции
            logger: logging.Logger | None = None    - Логгер для дебага программы
        """

        self.name = name
        self.dir = None  # Папка для хранения логов, картинок, истории этого запуска симуляции
        if logger is None:
            warnings.warn('Логгер не задан, печать логов будет отключена')
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
            self.set_logging(self.logger)

        self.logger.info(f"Инициализация симуляции {self.name}")

        if model is None:
            self.logger.error("Модель объекта управления не задана")
            raise AttributeError("Модель объекта управления не задана")
        else:
            self.model = model
            self.logger.info("Модель инициализирована")

        if control_system is None:
            self.logger.error("Система управления не задана")
            raise AttributeError("Система управления не задана")
        else:
            self.control_system = control_system
            self.logger.info("Система управления инициализирована")

        if historizer is None:
            self.logger.error("Система сбора данных не задана")
            raise AttributeError("Система сбора данных не задана")
        else:
            self.historizer = historizer
            self.logger.info("Система сбора данных инициализирована")
            self.historizer.create_folder(self.name)
            self.logger.debug(f"Создана папка хранения истории {self.historizer.dir}")

        try:
            assert float(tick_duration) > 0
            self.tick_duration = float(tick_duration)
            self.logger.info(f"Задана величина шага симуляции {float(tick_duration)}")
        except:
            self.logger.error(f"Некорректная величина шага симуляции {tick_duration}")
            raise AttributeError("Некорректное значение шага симуляции")

        self.time = 0

    def run(self, simulation_time: float):
        """
        run
        ---
        Запускает симуляцию на время simulation_time

        Аргументы:
            simulation_time:float     - Время на которое необходимо запустить математическое моделирование
        """

        self.logger.info(f"Запуск симуляции {self.name} с времени {self.time} на период {simulation_time}")
        start_time = self.time
        #
        while self.time <= start_time + simulation_time:
            self.tick()

    def tick(self):
        """
        tick
        ---
        Получение данных сенсоров текущего тика -> формирование управления на их основе ->
        -> запись управляющих воздействий -> обновление модели физической системы -> обновление времени системы

        + запись истории по всем сенсорам, управляющим воздействиям и реальным переменным физ. модели и системы управления

        Переменные:
            sensor_data: dict{name: value}              - Данные сенсоров модели, учитывают неидеальность измерений
            control_actions: dict{name: value}          - Данные управляющих воздействий, учитывают ограничения управления
            model_state: dict{name: value}              - Реальное состояние модели, используется для архива и аналитики, записаны все переменные
            control_system_state: dict{name: value}     - Реальное состояние системы управления, используется для архива и аналитики, записаны все переменные
        """

        self.logger.info(f"Обработка итерации симуляции для момента времени {self.time}")

        # Получаем данные с сенсоров модели за предыдущую итерацию
        self.logger.debug(f"Собираем данные сенсоров для момента времени {self.time}")
        sensor_data = self.model.read_sensors()

        # Передаём данные с сенсоров в систему управления, получаем управляющие воздействия
        self.control_system.load_sensor_data(sensor_data)
        self.control_system.compute(tick_duration=self.tick_duration)
        self.logger.debug(f"Собираем управляющие воздействия для момента времени {self.time}")
        control_actions = self.control_system.read_control_actions()

        self.model.load_variables(control_actions)

        # Получаем реальное состояние модели и системы управления
        self.logger.debug(f"Собираем реальное состояние физ. системы для момента времени {self.time}")
        model_state = self.model.get_state()
        self.logger.debug(f"Собираем реальное состояние системы управления для момента времени {self.time}")
        control_system_state = self.control_system.get_state()
        controllers_state = self.control_system.supervisor.controller_bank.get_state()
        estimators_state = self.control_system.supervisor.estimator_bank.get_state()

        # Записываем текущее состояние системы в модуль ведения истории
        self.logger.debug(f"Записываем историю для момента времени {self.time}")
        self.historizer.record(self.time, model_sensor_data=sensor_data, control_actions=control_actions,
                               model_state=model_state, control_system_state=control_system_state,
                               **controllers_state, **estimators_state)

        # Записываем управляющие воздействия в модель, делаем шаг симуляции
        self.logger.debug(f"Запускам шаг симуляции модели для момента времени {self.time}")

        self.model.compute(self.tick_duration)

        # Двигаем время
        self.time += self.tick_duration

    def set_logging(self, logger) -> None:
        # Базовая папка для логов
        base_log_dir = "logs"
        # Подпапка с текущей датой и временем запуска
        run_dir = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")} Simulation for {self.name}'
        self.dir = os.path.join(base_log_dir, run_dir)
        os.makedirs(self.dir, exist_ok=True)

        # Файл лога
        log_info_file = os.path.join(self.dir, f"{self.name}_info.log")
        log_warn_file = os.path.join(self.dir, f"{self.name}_warn.log")

        # Настраиваем детальный вывод в файл
        file_handler = logging.FileHandler(log_info_file, mode='w', encoding='UTF-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        file_handler.setLevel(logging.INFO)

        # Настраиваем отдельный вывод ошибок и предупреждений в файл
        error_handler = logging.FileHandler(log_warn_file, mode='w', encoding='UTF-8')
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s - '
            '%(pathname)s:%(lineno)d'
        ))
        error_handler.setLevel(logging.WARNING)

        # Создаем логгер
        # logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Добавляем обработчики
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)

        return None

