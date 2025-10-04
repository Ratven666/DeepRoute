from abc import ABC, abstractmethod

from deep_route.oil_well.OilWell import OilWell
from deep_route.oil_well.Section import Section


class TestABC(ABC):

    def __init__(self, oil_well: OilWell):
        self.oil_well = oil_well

    def start_test(self):
        total_result = {}
        for section in self.oil_well.sections:
            result_data = self.start_section_test(section)
            total_result[section.section_number] = result_data
        return total_result

    @abstractmethod
    def start_section_test(self, section: Section):
        pass

    def __str__(self):
        return f"{self.__class__.__name__} [oil_well={self.oil_well}]"
