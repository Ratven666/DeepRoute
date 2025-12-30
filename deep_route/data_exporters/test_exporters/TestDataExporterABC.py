from abc import ABC, abstractmethod

from deep_route.oil_well.OilWell import OilWell
from deep_route.tests.TestABC import TestABC


class TestDataExporterABC(ABC):

    def __init__(self, test_obj: TestABC):
        self.oil_well = test_obj.oil_well
        self.test_obj = test_obj
        self.test_result = self.test_obj.start_test()

    @abstractmethod
    def export_data(self, file_path, print_log=True):
        pass
