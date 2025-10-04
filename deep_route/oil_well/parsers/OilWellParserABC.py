from abc import ABC, abstractmethod


class OilWellParserABC(ABC):

    def __init__(self, file_path):
        self.file_path = file_path

    @abstractmethod
    def parse(self, oil_well):
        pass
