from math import degrees

import pandas as pd

from deep_route.data_exporters.test_exporters.ExcelTestDataExporterABC import ExcelTestDataExporterABC
from deep_route.tests.magnetometer.multi_station_magnetoneter_test.MSMTTest import MSMTTest


class TFDTTestExcelDataExporter(ExcelTestDataExporterABC):

    def __init__(self, test_obj: MSMTTest):
        super().__init__(test_obj)

    def _get_custom_df(self) -> pd.DataFrame:
        b_measured, b_theoretical = [], []
        delta_b, mse_db = [], []
        status_db = []
        dip_measured, dip_theoretical = [], []
        delta_dip, mse_dip = [], []
        status_dip = []
        total_status = []

        for section, result_data in self.test_result.items():
            result_data = result_data["earth_magnet_field_subsections_test"]
            for subsection, data in result_data.items():
                tfdt_db = data["TFDT_db"]
                tfdt_d_dip = data["TFDT_d_dip"]
                b_measured.append(subsection.measure.b_t)
                b_theoretical.append(self.test_obj.theoretical_b_total)
                delta_b.append(tfdt_db["delta_b"])
                mse_db.append(3 * tfdt_db["mse_db"])
                status_db.append(str(tfdt_db["is_correct"]))
                dip_measured.append(degrees(subsection.magnetic_dip))
                dip_theoretical.append(subsection.dip_ref)
                delta_dip.append(degrees(tfdt_d_dip["delta_theta"]))
                mse_dip.append(3 * degrees(tfdt_d_dip["mse_dtheta"]))
                status_dip.append(str(tfdt_d_dip["is_correct"]))
                total_status.append(str(tfdt_db["is_correct"] and tfdt_d_dip["is_correct"]))

        columns_names = ["b_measured", "b_theoretical" , "delta_b", "3*mse_db", "status_db",
                         "dip_measured", "dip_theoretical", "delta_dip", "3*mse_dip", "status_dip",
                         "total_status",
                         ]
        df = pd.DataFrame(list(zip(b_measured, b_theoretical, delta_b, mse_db, status_db,
                                   dip_measured, dip_theoretical, delta_dip, mse_dip, status_dip,
                                   total_status)),
                          columns=columns_names)
        return df

if __name__ == '__main__':
    from deep_route.base_geometry.Point import Point
    from deep_route.oil_well.OilWell import OilWell

    base_point = Point(x=457761.06, y=7602076.31, z=40.30)

    oil_well = OilWell(latitude=68.527570255,
                       longitude=79.964853136,
                       center_longitude=81,
                       m_delta=23.06,
                       dip_ref=82.78,
                       start_point=base_point,
                       )
    oil_well.import_oil_well_file(file_path="../../../src/raw_data.csv")
    oil_well.calculate_trace()

    msmt_test = MSMTTest(oil_well, theoretical_b_total=59923)

    exporter = TFDTTestExcelDataExporter(msmt_test)
    exporter.export_data('замеры.xlsx')