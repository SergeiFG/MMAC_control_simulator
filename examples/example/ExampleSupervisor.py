from basics import Supervisor


class ExampleSupervisor(Supervisor):

    def chose_estimator(self) -> None:
        # Эстиматор только один, поэтому всегда используем первый
        self.current_estimator = "Estimator"

    def choose_controller(self) -> None:
        # Выбор контроллера на основе показаний качества от эстиматоров, выбирается максимальный, имена параметров соответствуют именам контроллеров
        estimator = self.estimator_bank[self.current_estimator]
        controller_quality = estimator.read_sensors()
        chosen_controller = list(controller_quality.keys())[0]
        for key, value in controller_quality.items():
            if value > controller_quality[chosen_controller]:
                chosen_controller = key
        self.current_controller = chosen_controller
