from deep_route.oil_well.OilWell import OilWell

oil_well = OilWell()

print(oil_well)

oil_well.import_oil_well_file(file_path="src/raw_data.csv")

print(oil_well)


