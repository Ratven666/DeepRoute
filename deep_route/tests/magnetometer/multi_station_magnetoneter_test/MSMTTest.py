import math

import numpy as np

from deep_route.oil_well.Section import Section
from deep_route.tests.magnetometer.MagnetometerTestABC import MagnetometerTestABC
from deep_route.tests.magnetometer.earth_model_magnet_errors import BGGM_EARTH_MODEL_MAGNET_ERRORS
from deep_route.tests.magnetometer.iscwsa_magnitometrer_errors import ISCWSA_STANDART_MAGNETOMETER_ERRORS


class MSMTTest(MagnetometerTestABC):

    def __init__(self, oil_well, theoretical_b_total, k=3,
                 magnetometer_error_model=ISCWSA_STANDART_MAGNETOMETER_ERRORS,
                 earth_model_magnet_errors=BGGM_EARTH_MODEL_MAGNET_ERRORS):
        super().__init__(oil_well)
        self.theoretical_b_total = theoretical_b_total
        self.k = k
        self.magnetometer_error_model = magnetometer_error_model
        self.earth_model_magnet_errors = earth_model_magnet_errors

    def start_section_test(self, section):
        a = self._calk_a_matrix(section=section)
        l = self._calk_l_matrix(section=section)
        x = self._calk_x_matrix(a, l)
        magnetometer_corrections = {"mbx": float(x[0][0]),
                                    "mby": float(x[1][0]),
                                    "mbz": float(x[2][0]),
                                    "msx": float(x[3][0]),
                                    "msy": float(x[4][0]),
                                    "msz": float(x[5][0]),
                                    }
        mses_dict = self._calk_magnetometer_mses(a, l, x)
        corr_matrix = self._calk_correlation_matrix(a)
        test_result = self._calk_test_result(x)
        emfst = self._earth_magnet_field_subsections_test(section=section)
        result_data = {"magnetometer_corrections": magnetometer_corrections,
                       "mses_dict": mses_dict,
                       "correlation_matrix": corr_matrix,
                       "test_result": test_result,
                       "earth_magnet_field_subsections_test": emfst,
                       }
        return result_data

    def _calk_mse_db(self, subsection):
        mag_em = self.magnetometer_error_model
        em = self.earth_model_magnet_errors
        derivatives = self.get_derivatives(subsection)
        d_mbx = derivatives["db_mbx"]
        d_mby = derivatives["db_mby"]
        d_mbz = derivatives["db_mbz"]
        d_msx = derivatives["db_msx"]
        d_msy = derivatives["db_msy"]
        d_msz = derivatives["db_msz"]
        d_mfi = derivatives["dbd_mfi"]

        mse_db = ((d_mbx ** 2 * mag_em["s_mbx"] ** 2) +
                  (d_mby ** 2 * mag_em["s_mby"] ** 2) +
                  (d_mbz ** 2 * mag_em["s_mbz"] ** 2) +
                  (d_msx ** 2 * mag_em["s_msx"] ** 2) +
                  (d_msy ** 2 * mag_em["s_msy"] ** 2) +
                  (d_msz ** 2 * mag_em["s_msz"] ** 2) +
                  (d_mfi ** 2 * em["s_mfi"] ** 2)) ** 0.5
        return mse_db

    def _calk_mse_dtheta(self, subsection):
        mag_em = self.magnetometer_error_model
        em = self.earth_model_magnet_errors
        derivatives = self.get_derivatives(subsection)
        dd_mbx = derivatives["dd_mbx"]
        dd_mby = derivatives["dd_mby"]
        dd_mbz = derivatives["dd_mbz"]
        dd_msx = derivatives["dd_msx"]
        dd_msy = derivatives["dd_msy"]
        dd_msz = derivatives["dd_msz"]
        dd_mdi = derivatives["dd_mdi"]

        mse_dtheta = ((dd_mbx ** 2 * mag_em["s_mbx"] ** 2) +
                      (dd_mby ** 2 * mag_em["s_mby"] ** 2) +
                      (dd_mbz ** 2 * mag_em["s_mbz"] ** 2) +
                      (dd_msx ** 2 * mag_em["s_msx"] ** 2) +
                      (dd_msy ** 2 * mag_em["s_msy"] ** 2) +
                      (dd_msz ** 2 * mag_em["s_msz"] ** 2) +
                      (dd_mdi ** 2 * math.radians(em["s_mdi"]) ** 2)) ** 0.5
        return mse_dtheta

    def _earth_magnet_field_subsections_test(self, section):
        result_data = {}
        v = self._calk_v_matrix(section)
        v_db = v[::2]
        v_d_dip = v[1::2]
        for idx, subsection in enumerate(section):
            mse_db = self._calk_mse_db(subsection=subsection)
            mse_dtheta = self._calk_mse_dtheta(subsection=subsection)

            delta_b = subsection.measure.b_t - self.theoretical_b_total
            delta_theta = subsection.magnetic_dip - math.radians(subsection.dip_ref)
            tfdt_db = {"mse_db": mse_db,
                       "delta_b": delta_b,
                       "is_correct": -(self.k * mse_db) <= delta_b <= (self.k * mse_db),
                       }
            tfdt_d_dip = {"mse_dtheta": mse_dtheta,
                          "delta_b": delta_theta,
                          "is_correct": -(self.k * mse_dtheta) <= delta_theta <= (self.k * mse_dtheta),
                          }
            msmt_db = {"mse_db": mse_db,
                       "delta_db_v": float(v_db[idx]),
                       "is_correct": abs(float(v_db[idx])) <= self.k * mse_db,
                       }
            msmt_d_dip = {"mse_dtheta": self.theoretical_b_total * mse_dtheta,
                          "delta_d_dip_v": float(v_d_dip[idx]),
                          "is_correct": abs(float(v_d_dip[idx])) <= self.k * (self.theoretical_b_total * mse_dtheta),
                          }

            result_data[subsection] = {"TFDT_db": tfdt_db,
                                       "TFDT_d_dip": tfdt_d_dip,
                                       "MSMT_DB": msmt_db,
                                       "MSMT_D_DIP": msmt_d_dip,
                                       }
        return result_data

    def _calk_test_result(self, x):
        mag_em = self.magnetometer_error_model

        mbx_test = abs(x[0]) <= self.k * mag_em["s_mbx"]
        mby_test = abs(x[1]) <= self.k * mag_em["s_mby"]
        mbz_test = abs(x[2]) <= self.k * mag_em["s_mbz"]
        msx_test = abs(x[3]) <= self.k * mag_em["s_msx"]
        msy_test = abs(x[4]) <= self.k * mag_em["s_msy"]
        msz_test = abs(x[5]) <= self.k * mag_em["s_msz"]
        test_result = {"mbx_test": bool(mbx_test[0]),
                       "mby_test": bool(mby_test[0]),
                       "mbz_test": bool(mbz_test[0]),
                       "msx_test": bool(msx_test[0]),
                       "msy_test": bool(msy_test[0]),
                       "msz_test": bool(msz_test[0]),
                       }
        return test_result

    def _calk_a_matrix(self, section):
        a = []
        for subsection in section:
            derivatives = self.get_derivatives(subsection)
            a.append([derivatives["db_mbx"], derivatives["db_mby"], derivatives["db_mbz"],
                      derivatives["db_msx"], derivatives["db_msy"], derivatives["db_msz"]])
            a.append([derivatives["dd_mbx"], derivatives["dd_mby"], derivatives["dd_mbz"],
                      derivatives["dd_msx"], derivatives["dd_msy"], derivatives["dd_msz"]])
        return np.array(a)

    def _calk_l_matrix(self, section):
        l = []
        for subsection in section:
            db_i = subsection.measure.b_t - self.theoretical_b_total
            bt_i_dd_i = self.theoretical_b_total * (subsection.magnetic_dip - math.radians(subsection.dip_ref))
            l.append([db_i])
            l.append([bt_i_dd_i])
        return np.array(l)

    @staticmethod
    def _calk_x_matrix(a, l):
        n = a.T @ a
        q = np.linalg.inv(n)
        x = q @ a.T @ l
        return x

    def _calk_v_matrix(self, section):
        a = self._calk_a_matrix(section)
        l = self._calk_l_matrix(section)
        x = self._calk_x_matrix(a, l)
        v = l - a @ x
        return v

    @staticmethod
    def _calk_magnetometer_mses(a, l, x):
        v = l - a @ x
        vv = v.T @ v
        mu = (vv[0][0] / (len(v) - len(x))) ** 0.5
        q = np.linalg.inv(a.T @ a)
        diagonal_q = np.diag(q)
        mses = np.sqrt(diagonal_q) * mu
        mses_dict = {"mu": float(mu),
                     "v": v.flatten(),
                     "mse_mbx": float(mses[0]),
                     "mse_mby": float(mses[1]),
                     "mse_mbz": float(mses[2]),
                     "mse_msx": float(mses[3]),
                     "mse_msy": float(mses[4]),
                     "mse_msz": float(mses[5]),
                     }
        return mses_dict

    @staticmethod
    def _calk_correlation_matrix(a):
        n = a.T @ a
        q = np.linalg.inv(n)
        n = q.shape[0]
        corr_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                corr_matrix[i, j] = q[i, j] / np.sqrt(q[i, i] * q[j, j])
        return corr_matrix


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

    get_test = MSMTTest(oil_well, theoretical_b_total=59923)
    result = get_test.start_test()
    # print(result)

    for section, result_data in result.items():
        print(section, "\n")
        for type_, data in result_data.items():
            print("\n", type_)
            print(data, sep="\n")
