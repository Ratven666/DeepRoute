import pandas as pd

from deep_route.data_exporters.test_exporters.ExcelTestDataExporterABC import ExcelTestDataExporterABC
from deep_route.tests.accelerometer.gravity_error_test.GETTest import GETTest


class GETTestExcelDataExporter(ExcelTestDataExporterABC):

    def __init__(self, test_obj: GETTest):
        super().__init__(test_obj)

    def _get_custom_df(self) -> pd.DataFrame:
        g_t_measure, g_t_theoretical = [], []
        delta_g, mse_dg = [], []
        status = []
        for section, result_data in self.test_result.items():
            for type_, data in result_data.items():
                for result in data:
                    subsection = result["subsection"]
                    g_t_measure.append(subsection.measure.g_t)
                    g_t_theoretical.append(self.test_obj.theoretical_gravity)
                    delta_g.append(result["delta_g"])
                    mse_dg.append(3 * result["mse_dg"])
                    status.append(str(result["is_correct"]))
        columns_names = ["g_t_measure", "g_t_theoretical" , "delta_g", "3*mse_dg",
                         "status"]
        df = pd.DataFrame(list(zip(g_t_measure, g_t_theoretical,
                                   delta_g, mse_dg,
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

    get_test = GETTest(oil_well, theoretical_gravity=1.001878)

    exporter = GETTestExcelDataExporter(get_test)
    exporter.export_data('замеры.xlsx')