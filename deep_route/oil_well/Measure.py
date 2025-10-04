

class Measure:

    def __init__(self, measure_number, sec_number, depth,
                 g_x, g_y, g_z,
                 b_x, b_y, b_z,
                 ):
        self.measure_number = measure_number
        self.sec_number = sec_number
        self.depth = depth
        self.g_x, self.g_y, self.g_z = g_x, g_y, g_z
        self.b_x, self.b_y, self.b_z = b_x, b_y, b_z

    def __str__(self):
        return f"{self.__class__.__name__} {self.measure_number} {self.sec_number} {self.depth}"

    def __repr__(self):
        return f"{self.__class__.__name__} {self.measure_number} {self.sec_number} {self.depth}"