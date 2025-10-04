from abc import ABC, abstractmethod


class OilWellPlotterABC(ABC):

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def plot(self, oil_well):
        pass
