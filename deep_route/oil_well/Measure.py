

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
        self.g_x, self.g_y, self.g_z = g_x, g_y, g_z
        self.b_x, self.b_y, self.b_z = b_x, b_y, b_z
        self.g_t = (self.g_x**2 + self.g_y**2 + self.g_z**2) ** 0.5

    def __str__(self):
        return (f"{self.__class__.__name__} [m_n={self.measure_number}, sec_n={self.sec_number}, "
                f"depth={self.depth}, length={self.length}, "
                f"G=({self.g_x:.3f}, {self.g_y:.3f}, {self.g_z:.3f}), "
                f"B=({self.b_x}, {self.b_y}, {self.b_z})]")

    def __repr__(self):
        return f"{self.__class__.__name__} {self.measure_number} {self.sec_number}"