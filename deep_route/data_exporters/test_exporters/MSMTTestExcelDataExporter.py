import pandas as pd

from deep_route.data_exporters.test_exporters.ExcelTestDataExporterABC import ExcelTestDataExporterABC
from deep_route.tests.magnetometer.multi_station_magnetoneter_test.MSMTTest import MSMTTest


class MSMTTestExcelDataExporter(ExcelTestDataExporterABC):

    def __init__(self, test_obj: MSMTTest):
        super().__init__(test_obj)

    def _get_custom_df(self) -> pd.DataFrame:
        delta_db_v, mse_db = [], []
        status_db = []
        delta_d_dip_v = []
        mse_dtheta = []
        status_d_dip = []
        total_status = []


        for section, result_data in self.test_result.items():
            result_data = result_data["earth_magnet_field_subsections_test"]
            for subsection, data in result_data.items():
                msmt_db = data["MSMT_DB"]
                msmt_d_dip = data["MSMT_D_DIP"]

                delta_db_v.append(msmt_db["delta_db_v"])
                mse_db.append(3 * msmt_db["mse_db"])
                status_db.append(str(msmt_db["is_correct"]))
                delta_d_dip_v.append(msmt_d_dip["delta_d_dip_v"])
                mse_dtheta.append(3 * msmt_d_dip["mse_dtheta"])
                status_d_dip.append(str(msmt_d_dip["is_correct"]))
                total_status.append(str(msmt_db["is_correct"] and msmt_d_dip["is_correct"]))

        columns_names = ["v(B)", "3*mse_db(B)" , "status_db",
                         "v(B(t)*Dip)", "B(t)*3σ(Dip)", "status_d_dip",
                         "total_status",
                         ]
        df = pd.DataFrame(list(zip(delta_db_v, mse_db, status_db,
                                   delta_d_dip_v, mse_dtheta, status_d_dip,
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

    exporter = MSMTTestExcelDataExporter(msmt_test)
    exporter.export_data('замеры.xlsx')