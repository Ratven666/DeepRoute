import os

from deep_route.data_exporters.test_exporters.GETTestExcelDataExporter import GETTestExcelDataExporter
from deep_route.data_exporters.test_exporters.MSATTestExcelDataExporter import MSATTestExcelDataExporter
from deep_route.data_exporters.test_exporters.MSMTTestExcelDataExporter import MSMTTestExcelDataExporter
from deep_route.data_exporters.test_exporters.TFDTTestExcelDataExporter import TFDTTestExcelDataExporter
from deep_route.tests.accelerometer.gravity_error_test.GETTest import GETTest
from deep_route.tests.accelerometer.iscwsa_gravity_errors import ISCWSA_GRAVITY_ERRORS
from deep_route.tests.accelerometer.multi_station_accelerometer_test.MSATTest import MSATTest
from deep_route.tests.magnetometer.earth_model_magnet_errors import BGGM_EARTH_MODEL_MAGNET_ERRORS
from deep_route.tests.magnetometer.iscwsa_magnitometrer_errors import ISCWSA_STANDART_MAGNETOMETER_ERRORS
from deep_route.tests.magnetometer.multi_station_magnetoneter_test.MSMTTest import MSMTTest


class ExcelTotalTestExporter:

    def __init__(self, oil_well,
                 theoretical_gravity, theoretical_b_total,
                 k=3,
                 gravity_error_model=ISCWSA_GRAVITY_ERRORS,
                 magnetometer_error_model=ISCWSA_STANDART_MAGNETOMETER_ERRORS,
                 earth_model_magnet_errors=BGGM_EARTH_MODEL_MAGNET_ERRORS,
                 ):
        self.oil_well = oil_well
        self.tests = {"GET": GETTest(oil_well, theoretical_gravity=theoretical_gravity,
                                     k=k, gravity_error_model=gravity_error_model),
                      "MSAT": MSATTest(oil_well, theoretical_gravity=theoretical_gravity,
                                       k=k, gravity_error_model=gravity_error_model),
                      "MSMT": MSMTTest(oil_well, theoretical_b_total=theoretical_b_total,
                                       k=k, magnetometer_error_model=magnetometer_error_model,
                                       earth_model_magnet_errors=earth_model_magnet_errors),
                      }
        self.exporters = {"GET": GETTestExcelDataExporter(self.tests["GET"]),
                          "MSAT": MSATTestExcelDataExporter(self.tests["MSAT"]),
                          "TFDT": TFDTTestExcelDataExporter(self.tests["MSMT"]),
                          "MSMT": MSMTTestExcelDataExporter(self.tests["MSMT"]),
                          }

    def export_data(self, file_path=".", print_log=True):
        for type_, exporter in self.exporters.items():
            path = os.path.join(file_path, f"{type_}.xlsx")
            exporter.export_data(path, print_log=print_log)

if __name__ == "__main__":
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

    exporter = ExcelTotalTestExporter(oil_well,
                                      theoretical_gravity=1.001878,
                                      theoretical_b_total=59923,
                                      )

    exporter.export_data()