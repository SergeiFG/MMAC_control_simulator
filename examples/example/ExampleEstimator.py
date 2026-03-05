from basics import FunctionalBlock, Parameter, ParameterSet
from modules.estimators import RangeEstimator
from numbers import Number
import random


# Функция для получения словаря с границами контроллеров
def controller_boundaries(boundary):
    return {
        "Controller_min": {"Level": (None, -boundary)},
        "Controller_middle": {"Level": (-boundary, boundary)},
        "Controller_max": {"Level": (boundary, None)}
    }


def get_estimator(logger, boundary) -> RangeEstimator:
    return RangeEstimator(logger=logger,
                          process_parameters=['Level'],
                          controller_regions=controller_boundaries(boundary)
                          )

