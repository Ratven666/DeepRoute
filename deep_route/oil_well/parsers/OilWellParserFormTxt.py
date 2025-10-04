import pandas as pd

from deep_route.oil_well.Measure import Measure
from deep_route.oil_well.Section import Section
from deep_route.oil_well.SubSection import SubSection
from deep_route.oil_well.parsers.OilWellParserABC import OilWellParserABC


class OilWellParserFormTxt(OilWellParserABC):
    def parse(self, oil_well):
        measure_df = pd.read_csv(self.file_path, sep=";")
        sections_dict = self._init_sections(measure_df, oil_well)
        self._init_subsections(measure_df=measure_df, sections_dict=sections_dict)
        for section_number, section in sections_dict.items():
            oil_well.add_section(section)

    @staticmethod
    def _init_sections(measure_df, oil_well):
        section_unique_numbers = measure_df["Sec_number"].unique()
        sections_dict = {}
        for section_number in section_unique_numbers:
            section = Section(section_number=section_number, oil_well=oil_well)
            sections_dict[int(section_number)] = section
        return sections_dict


    def _init_subsections(self, measure_df, sections_dict):
        previous_depth = 0
        for index, raw_measure in measure_df.iterrows():
            measure = self._get_measure(raw_measure, previous_depth)
            previous_depth = measure.depth
            section = sections_dict[measure.sec_number]
            subsection = SubSection(measure=measure, section=section)
            section.add_subsection(subsection)

    @staticmethod
    def _get_measure(raw_measure, previous_depth):
        measure_number = int(raw_measure["Measure_number"])
        sec_number = int(raw_measure["Sec_number"])
        depth = float(raw_measure["Depth"])
        length = depth - previous_depth
        g_x, g_y, g_z = float(raw_measure["Gx"]), float(raw_measure["Gy"]), float(raw_measure["Gz"])
        b_x, b_y, b_z = int(raw_measure["Bx"]), int(raw_measure["By"]), int(raw_measure["Bz"])
        measure = Measure(measure_number=measure_number,
                          sec_number=sec_number,
                          depth=depth,
                          length=length,
                          g_x=g_x,
                          g_y=g_y,
                          g_z=g_z,
                          b_x=b_x,
                          b_y=b_y,
                          b_z=b_z,
                          )
        return measure




        # with open(self.file_path, "rt", encoding="UTF-8") as file:
        #     file.readline()
        #     for line in file:
        #         line = line.strip().split(";")
        #         print(line)

