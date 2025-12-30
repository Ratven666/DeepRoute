import pandas as pd

from deep_route.data_exporters.test_exporters.ExcelTestDataExporterABC import ExcelTestDataExporterABC
from deep_route.tests.accelerometer.multi_station_accelerometer_test.MSATTest import MSATTest


class MSATTestExcelDataExporter(ExcelTestDataExporterABC):

    def __init__(self, test_obj: MSATTest):
        super().__init__(test_obj)

    def _get_custom_df(self) -> pd.DataFrame:
        v, mse_dg = [], []
        status = []
        for section, result_data in self.test_result.items():
            result_data = result_data["subsection_test"]
            for subsection, data in result_data.items():
                v.append(data["v"])
                mse_dg.append(3 * data["mse_dg"])
                status.append(str(data["result"]))

        columns_names = ["v", "3*mse_dg" , "status"]
        df = pd.DataFrame(list(zip(v, mse_dg,
                                   status,
                                   )),
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

    msat_test = MSATTest(oil_well, theoretical_gravity=1.001878)

    exporter = MSATTestExcelDataExporter(msat_test)
    exporter.export_data('замеры.xlsx')