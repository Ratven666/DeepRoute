

class Section:

    def __init__(self, section_number):
        self.section_number = section_number
        self.subsections = []

    def add_subsection(self, subsection):
        self.subsections.append(subsection)

    def __str__(self):
        return f"{self.__class__.__name__} {self.section_number} len={len(self.subsections)}"

    def __repr__(self):
        return f"{self.__class__.__name__} {self.section_number} ({len(self.subsections)})"
