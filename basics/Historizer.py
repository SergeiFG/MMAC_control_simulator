import os
from datetime import datetime
from numbers import Number
import pandas as pd


class Historizer:
    """
    Historizer
    ---
    Класс для записи истории изменения значений во время симуляции

    """

    def __init__(self):
        self.name = None
        self.dir = None
        self.records: dict[str, pd.DataFrame] = {}

    def create_folder(self, name):
        self.name = name
        # Базовая папка для записи истории
        base_log_dir = "results"
        # Подпапка с текущей датой и временем запуска
        run_dir = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")} Simulation for {self.name}'
        self.dir = os.path.join(base_log_dir, run_dir)
        os.makedirs(self.dir, exist_ok=True)

    def record(self, timestamp: float, **kwargs: dict[str, Number | str]):
        if self.name is None or self.dir is None:
            raise AttributeError('Не указан путь к папке для записи истории')

        for table_name, data in kwargs.items():
            # Добавляем в словарь хранимых таблиц, если новая таблица
            if table_name not in self.records.keys():
                self.records[table_name] = pd.DataFrame(columns=["time"] + list(data.keys()))

            # Обрабатываем новые данные
            row = {key: value for key, value in data.items()}
            row.update({"time": timestamp})
            data_df = pd.DataFrame([row])

            # Добавляем новые столбцы, если появились новые параметры
            for col in data_df.columns:
                if col not in self.records[table_name].columns:
                    self.records[table_name][col] = None

            # Добавляем новую строку в таблицу
            self.records[table_name] = pd.concat([self.records[table_name], data_df], ignore_index=True)

    def save_history(self):

        for name, df in self.records.items():
            df.to_csv(f"{self.dir}/{name}.csv", index=False)



