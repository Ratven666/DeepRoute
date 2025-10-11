import math

import numpy as np

from deep_route.oil_well.Section import Section
from deep_route.tests.magnetometer.MagnetometerTestABC import MagnetometerTestABC


class MSMTTest(MagnetometerTestABC):

    def __init__(self, oil_well, theoretical_b_total):
        super().__init__(oil_well)
        self.theoretical_b_total = theoretical_b_total

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
        result_data = {"magnetometer_corrections": magnetometer_corrections,
                       "mses_dict": mses_dict,
                       "correlation_matrix": corr_matrix,
                       }
        return result_data

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
