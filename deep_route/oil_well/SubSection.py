import math

from deep_route.base_geometry.Point import Point
from deep_route.oil_well.Measure import Measure


class SubSection:

    def __init__(self, measure: Measure, section=None):
        self.measure = measure
        self.parent = section
        self.number = measure.measure_number
        self.magnetic_azimuth, self.zenith = self._calk_directions()
        self.length = measure.length
        self.azimuth = None
        self.dx, self.dy, self.dz = None, None, None
        self.start_point, self.end_point = None, None

    def calculate_azimuth(self,  m_delta, m_gamma):
        self.azimuth = self.magnetic_azimuth + math.radians(m_delta - m_gamma)

    def calculate_subsection(self):
        self.dx, self.dy, self.dz = self._calk_coordinate_increments()
        self.start_point, self.end_point = self._calk_borders_points()

    def _calk_directions(self):
        t_1 = self.measure.g_t * (self.measure.b_y * self.measure.g_x - self.measure.b_x * self.measure.g_y)
        t_2 = self.measure.b_z * (self.measure.g_x ** 2 + self.measure.g_y **2)
        t_3 = self.measure.g_z * (self.measure.g_x * self.measure.b_x + self.measure.g_y * self.measure.b_y)
        magnetic_azimuth = (math.atan2(t_1, (t_2 - t_3)) + math.tau) % math.tau
        zenith = math.acos(self.measure.g_z / self.measure.g_t)
        return magnetic_azimuth, zenith

    def _calk_coordinate_increments(self):
        # next_subsection = self.parent.get_subsection_by_number(self.number + 1)
        # next_azimuth, next_zenith = (next_subsection.azimuth, next_subsection.zenith) \
        #     if next_subsection \
        #     else (self.azimuth,  self.zenith)
        # avr_zenith = (self.zenith + next_zenith) / 2
        # avr_azimuth = (self.azimuth + next_azimuth) / 2
        previous_subsection = self.parent.get_subsection_by_number(self.number - 1)
        if previous_subsection is None:
            previous_azimuth = self.azimuth
            previous_zenith = self.zenith
        else:
            previous_azimuth = previous_subsection.azimuth
            previous_zenith = previous_subsection.zenith
        avr_zenith = (self.zenith + previous_zenith) / 2
        avr_azimuth = (self.azimuth + previous_azimuth) / 2
        dx = self.length * math.sin(avr_zenith) * math.sin(avr_azimuth)
        dy = self.length * math.sin(avr_zenith) * math.cos(avr_azimuth)
        dz = -self.length * math.cos(avr_zenith)
        return dx, dy, dz

    def _calk_borders_points(self):
        previous_subsection = self.parent.get_subsection_by_number(self.number - 1)
        if previous_subsection:
            start_point = previous_subsection.end_point
        else:
            start_point = self.parent.get_start_point()
        end_point = Point(x=start_point.x + self.dx,
                          y=start_point.y + self.dy,
                          z=start_point.z + self.dz,
                          )
        return start_point, end_point


    def __str__(self):
        return (f"{self.__class__.__name__} {self.number} [M={math.degrees(self.magnetic_azimuth):.4f},"
                f"A={math.degrees(self.azimuth):.4f}, "
                f"Z={math.degrees(self.zenith):.4f}, "
                f"S={self.length:.4f}, "
                f"dx={self.dx:.4f}, dy={self.dy:.4f}, dz={self.dz:.4f}, "
                f"points=[{repr(self.start_point)}-{repr(self.end_point)}]]")
