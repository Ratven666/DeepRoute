import pandas as pd

from deep_route.base_geometry.Point import Point
from deep_route.oil_well.OilWell import OilWell
from deep_route.tests.accelerometer.multi_station_accelerometer_test.MSATTest import MSATTest
from deep_route.tests.magnetometer.multi_station_magnetoneter_test.MSMTTest import MSMTTest

base_point = Point(x=457761.06, y=7602076.31, z=40.30)

oil_well = OilWell(latitude=68.527570255,
                   longitude=79.964853136,
                   center_longitude=81,
                   m_delta=23.06,
                   dip_ref=82.78,
                   start_point=base_point,
                   )
oil_well.import_oil_well_file(file_path="src/raw_data.csv")
oil_well.calculate_trace()

# oil_well.print_data()

# print(base_point)

# oil_well.plot()

# msat_test = MSATTest(oil_well, theoretical_gravity=1.001878)
# result = msat_test.start_test()
# print(result)
#
# for n, data in result.items():
#     print(n)
#     df = pd.DataFrame(data["correlation_matrix"])
#     print(df)

msmt_test = MSMTTest(oil_well, theoretical_b_total=59923)
result = msmt_test.start_test()
print(result)

for v in result[2]["mses_dict"]["v"]:
    print(v)

# for n, data in result.items():
#     print(n)
#     df = pd.DataFrame(data["correlation_matrix"])
#     print(df)

