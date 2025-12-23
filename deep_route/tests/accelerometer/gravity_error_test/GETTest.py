from deep_route.tests.TestABC import TestABC
from deep_route.tests.accelerometer.AccelerometerTestABC import AccelerometerTestABC
from deep_route.tests.accelerometer.iscwsa_gravity_errors import ISCWSA_GRAVITY_ERRORS


class GETTest(AccelerometerTestABC):

    def __init__(self, oil_well, theoretical_gravity=1., k=3, error_model=ISCWSA_GRAVITY_ERRORS):
        super().__init__(oil_well)
        self.theoretical_gravity = theoretical_gravity
        self.error_model = error_model
        self.k = k

    def get_mse_dg(self, subsection):
        em = self.error_model
        (derivative_abx, derivative_aby, derivative_abz,
         derivative_asx, derivative_asy, derivative_asz,
         derivative_gt) = self.get_derivatives(subsection)
        mse_dg = ((derivative_abx ** 2 * em["s_abx"] ** 2) +
                  (derivative_aby ** 2 * em["s_aby"] ** 2) +
                  (derivative_abz ** 2 * em["s_abz"] ** 2) +
                  (derivative_asx ** 2 * em["s_asx"] ** 2) +
                  (derivative_asy ** 2 * em["s_asy"] ** 2) +
                  (derivative_asz ** 2 * em["s_asz"] ** 2)) ** 0.5
        return mse_dg



    def start_section_test(self, section):
        result_data = {"GET_test": []}
        for subsection in section:
            mse_dg = self.get_mse_dg(subsection)
            delta_g = subsection.measure.g_t - self.theoretical_gravity
            data = {"subsection": subsection,
                    "mse_dg": mse_dg,
                    "delta_g": delta_g,
                    "is_correct": -(self.k * mse_dg) <= delta_g <= (self.k * mse_dg),
                    }
            result_data["GET_test"].append(data)
        return result_data


if __name__ == '__main__':
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
    oil_well.import_oil_well_file(file_path="../../../../src/raw_data.csv")
    oil_well.calculate_trace()

    get_test = GETTest(oil_well, theoretical_gravity=1.001878)
    result = get_test.start_test()
    print(result)
    for section, result_data in result.items():
        print(section, "\n\n")
        for type_, data in result_data.items():
            print(*data, sep="\n")

