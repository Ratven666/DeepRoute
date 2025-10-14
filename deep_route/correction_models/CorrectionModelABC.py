from abc import ABC, abstractmethod
from copy import deepcopy


class CorrectionModelABC(ABC):

    def __init__(self, oil_well, *args, **kwargs):
        self.oil_well = oil_well
        self.args = args
        self.kwargs = kwargs

    @abstractmethod
    def calculate_measure_correction(self):
        pass

    def calculate_correction(self, inplace=False):
        if not inplace:
            self.oil_well = deepcopy(self.oil_well)
        self.calculate_measure_correction()
        self.oil_well.calculate_trace()
        return self.oil_well
