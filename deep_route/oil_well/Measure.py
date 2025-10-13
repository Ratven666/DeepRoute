

class Measure:

    def __init__(self, measure_number, sec_number,
                 depth, length,
                 g_x, g_y, g_z,
                 b_x, b_y, b_z,
                 ):
        self.measure_number = measure_number
        self.sec_number = sec_number
        self.depth = depth
        self.length = length
        self._g_x, self._g_y, self._g_z = g_x, g_y, g_z
        self._b_x, self._b_y, self._b_z = b_x, b_y, b_z
        self.correction = {"g_x": 0, "g_y": 0, "g_z": 0,
                           "b_x": 0, "b_y": 0, "b_z": 0,
                           }

    @property
    def g_x(self):
        return self._g_x + self.correction["g_x"]

    @property
    def g_y(self):
        return self._g_y + self.correction["g_y"]

    @property
    def g_z(self):
        return self._g_z + self.correction["g_z"]

    @property
    def b_x(self):
        return self._b_x + self.correction["b_x"]

    @property
    def b_y(self):
        return self._b_y + self.correction["b_y"]

    @property
    def b_z(self):
        return self._b_z + self.correction["b_z"]

    @property
    def b_t(self):
        return (self.b_x**2 + self.b_y**2 + self.b_z**2) ** 0.5

    @property
    def g_t(self):
        return (self.g_x**2 + self.g_y**2 + self.g_z**2) ** 0.5


    def __str__(self):
        return (f"{self.__class__.__name__} [m_n={self.measure_number}, sec_n={self.sec_number}, "
                f"depth={self.depth}, length={self.length}, "
                f"G=({self._g_x:.3f}, {self._g_y:.3f}, {self._g_z:.3f}), "
                f"B=({self._b_x}, {self._b_y}, {self._b_z}), "
                f"corrections={self.correction})]")

    def __repr__(self):
        return f"{self.__class__.__name__} {self.measure_number} {self.sec_number}"