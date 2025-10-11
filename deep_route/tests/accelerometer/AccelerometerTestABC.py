from abc import abstractmethod

from deep_route.oil_well.Measure import Measure
from deep_route.oil_well.Section import Section
from deep_route.oil_well.SubSection import SubSection
from deep_route.tests.TestABC import TestABC


class AccelerometerTestABC(TestABC):

    @abstractmethod
    def start_section_test(self, section: Section):
        pass

    @staticmethod
    def get_derivatives(sub_section: SubSection):
        measure = sub_section.measure
        derivative_abx = measure.g_x / measure.g_t
        derivative_aby = measure.g_y / measure.g_t
        derivative_abz = measure.g_z / measure.g_t
        derivative_asx = (measure.g_x ** 2) / measure.g_t
        derivative_asy = (measure.g_y ** 2) / measure.g_t
        derivative_asz = (measure.g_z ** 2) / measure.g_t
        derivative_gt = -1
        return (derivative_abx, derivative_aby, derivative_abz,
                derivative_asx, derivative_asy, derivative_asz,
                derivative_gt)