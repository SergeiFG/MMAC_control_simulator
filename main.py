from basics import SimulationEngine, Historizer
import logging
from basics import ColoredFormatter

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
# Создание симуляции
test = SimulationEngine(
    name='Test',
    model=0,
    control_system=0,
    historizer=historizer,
    tick_duration=1,
    logger=logger
)

historizer.save_history()

