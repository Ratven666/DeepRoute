from deep_route.base_geometry.Point import Point
from deep_route.oil_well.OilWell import OilWell

base_point = Point(x=457761.06, y=7602076.31, z=40.30)

oil_well = OilWell(latitude=68.527570255,
                   longitude=79.964853136,
                   center_longitude=81,
                   start_point=base_point,
                   )
oil_well.import_oil_well_file(file_path="src/raw_data.csv")
oil_well.calculate_trace()

oil_well.print_data()

print(base_point)

oil_well.plot()

