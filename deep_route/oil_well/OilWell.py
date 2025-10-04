from deep_route.oil_well.parsers.OilWellParserFormTxt import OilWellParserFormTxt


class OilWell:

    def __init__(self):
        self.sections = []

    def add_section(self, section):
        self.sections.append(section)

    def import_oil_well_file(self, file_path, parser=OilWellParserFormTxt):
        parser = parser(file_path)
        parser.parse(oil_well=self)
        return self

    def __str__(self):
        return f"{self.__class__.__name__} {self.sections}"
