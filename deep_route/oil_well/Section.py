class Section:

    def __init__(self, section_number, oil_well=None):
        self.parent = oil_well
        self.start_point = None
        self.section_number = section_number
        self.subsections = {}

    def add_subsection(self, subsection):
        self.subsections[subsection.number] = subsection

    def get_subsection_by_number(self, number):
        if self.parent is not None:
            return self.parent.get_subsection_by_number(number)
        return self.subsections.get(number, None)

    def get_start_point(self):
        if self.start_point is not None:
            return self.start_point
        else:
            return self.parent.start_point

    def calk_real_azimuth(self, m_delta, m_gamma):
        for subsection in self.subsections.values():
            subsection.calculate_azimuth(m_delta, m_gamma)

    def calculate_trace(self):
        m_delta = self.parent.m_delta
        m_gamma = self.parent.m_gamma
        for subsection in self.subsections.values():
            subsection.calculate_subsection(m_delta=m_delta, m_gamma=m_gamma)

    @property
    def dip_ref(self):
        return self.parent.dip_ref

    def __str__(self):
        return f"{self.__class__.__name__} {self.section_number} len={len(self.subsections)}"

    def __repr__(self):
        return f"{self.__class__.__name__} {self.section_number} ({len(self.subsections)})"

    def __iter__(self):
        return iter(self.subsections.values())

    def __len__(self):
        return len(self.subsections)

    def __hash__(self):
        return hash(self.section_number)

    def __eq__(self, other):
        return self.section_number == other.section_number
