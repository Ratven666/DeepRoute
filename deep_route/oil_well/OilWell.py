import math

from deep_route.base_geometry.Point import Point
from deep_route.correction_models.CorrectionModelABC import CorrectionModelABC
from deep_route.oil_well.parsers.OilWellParserFormTxt import OilWellParserFormTxt
from deep_route.oil_well.plotters.OilWellPlotterMPL import OilWellPlotterMPL


class OilWell:

    def __init__(self,
                 latitude,
                 longitude,
                 center_longitude,
                 m_delta,
                 dip_ref,
                 start_point=Point(x=0, y=0),
                 ):
        self.latitude = latitude
        self.longitude = longitude
        self.dip_ref = dip_ref
        self.center_longitude = center_longitude
        self.m_delta = m_delta
        self.m_gamma = self._calk_magnetic_corrections()
        self.start_point = start_point
        self.sections = []

    def add_section(self, section):
        self.sections.append(section)

    def import_oil_well_file(self, file_path, parser=OilWellParserFormTxt):
        parser = parser(file_path)
        parser.parse(oil_well=self)
        self._calk_real_azimuths()
        return self

    def get_subsection_by_number(self, number):
        for section in self.sections:
            subsection = section.subsections.get(number, None)
            if subsection is not None:
                return subsection
        return None

    def _calk_magnetic_corrections(self):
        m_gamma = (self.longitude - self.center_longitude) * math.sin(math.radians(self.latitude))
        return m_gamma

    def _calk_real_azimuths(self):
        for section in self.sections:
            section.calk_real_azimuth(self.m_delta, self.m_gamma)

    def calculate_trace(self):
        self._calk_real_azimuths()
        for section in self.sections:
            section.calculate_trace()

    def plot(self, *args, plotter=OilWellPlotterMPL, is_show=True, **kwargs):
        plotter = plotter(*args, is_show=is_show, **kwargs)
        fig_ax = plotter.plot(oil_well=self)
        return fig_ax

    def calculate_correction(self, *args, correction_model,
                             inplace=False, **kwargs):
        correction_model = correction_model(self, *args, **kwargs)
        oil_well = correction_model.calculate_correction(inplace=inplace)
        return oil_well

    def __str__(self):
        return f"{self.__class__.__name__} [start_point={self.start_point}, sections={self.sections}]"

    def __iter__(self):
        return iter(self.sections)

    def print_data(self):
        print(self)
        for section in self.sections:
            print(f"\t{section}")
            for subsection in section:
                print(f"\t\t{subsection}")
