from basics import Supervisor


class RSTSupervisor(Supervisor):
    def chose_estimator(self) -> None:
        self.current_estimator = "RSTEstimator"

    def choose_controller(self) -> None:
        estimator = self.estimator_bank[self.current_estimator]
        controller_quality = estimator.read_sensors()
        self.current_controller = max(controller_quality, key=controller_quality.get)
