from abc import abstractmethod
from math import degrees

import pandas as pd
import tabulate

from deep_route.data_exporters.test_exporters.TestDataExporterABC import TestDataExporterABC


class ExcelTestDataExporterABC(TestDataExporterABC):

    @abstractmethod
    def _get_custom_df(self):
        pass

    def _get_result_df(self) -> pd.DataFrame:
        base_df = self._get_base_df()
        custom_df = self._get_custom_df()
        result_df = pd.concat([base_df, custom_df], axis=1)
        return result_df

    def _get_base_df(self) -> pd.DataFrame:
        subsection_number, section_number = [], []
        md, length = [], []
        azimuth, zenith, tool_face = [], [], []
        for section in self.oil_well:
            for subsection in section:
                subsection_number.append(subsection.number)
                section_number.append(int(section.section_number))
                md.append(subsection.measure.depth)
                length.append(subsection.length)
                azimuth.append(degrees(subsection.azimuth))
                zenith.append(degrees(subsection.zenith))
                tool_face.append(degrees(subsection.tool_face))
        columns_names = ["measure_number", "section_number" , "MD", "length",
                         "azimuth_deg", "zenith_deg", "tool_face_deg"]
        df = pd.DataFrame(list(zip(subsection_number, section_number, md, length,
                                   azimuth, zenith, tool_face,
                                   )),
                          columns=columns_names)
        return df

    def print_log(self, df):
        print("\n", self.test_obj.__class__.__name__)
        print(tabulate.tabulate(df, headers="keys", tablefmt='pretty'))

    def export_data(self, file_path, print_log=True):
        df = self._get_result_df()
        if print_log:
            self.print_log(df)
        file_path = file_path if file_path.endswith(".xlsx") else file_path + ".xlsx"
        sheet_name = self.test_obj.__class__.__name__
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
                merge_cells=True,
            )
