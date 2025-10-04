import numpy as np

from deep_route.tests.accelerometer.AccelerometerTestABC import AccelerometerTestABC


class MSATTest(AccelerometerTestABC):

    def __init__(self, oil_well, theoretical_gravity=1.):
        super().__init__(oil_well)
        self.theoretical_gravity = theoretical_gravity
        # self.accel_corrections = {}

    def start_section_test(self, section):
        a = self._calk_a_matrix(section=section)
        l = self._calk_l_matrix(section=section)
        x = self._calk_x_matrix(a, l)
        accel_corrections = {"abx": float(x[0][0]),
                             "aby": float(x[1][0]),
                             "abz": float(x[2][0]),
                             "asx": float(x[3][0]),
                             "asy": float(x[4][0]),
                             }
        mses_dict = self._calk_accel_mses(a, l, x)
        corr_matrix = self._calk_correlation_matrix(a)
        result_data = {"accel_corrections": accel_corrections,
                       "mses_dict": mses_dict,
                       "correlation_matrix": corr_matrix,
                       }
        return result_data

    def _calk_a_matrix(self, section):
        a = []
        for subsection in section:
            (derivative_abx, derivative_aby, derivative_abz,
             derivative_asx, derivative_asy, derivative_asz,
             derivative_gt) = self.get_accel_derivatives(subsection.measure)
            a.append([derivative_abx, derivative_aby, derivative_abz,
                      derivative_asx, derivative_asy])
        return np.array(a)

    def _calk_l_matrix(self, section):
        l = []
        for subsection in section:
            l.append([subsection.measure.g_t - self.theoretical_gravity])
        return np.array(l)

    @staticmethod
    def _calk_x_matrix(a, l):
        n = a.T @ a
        q = np.linalg.inv(n)
        x = q @ a.T @ l
        return x

    @staticmethod
    def _calk_accel_mses(a, l, x):
        v = l - a @ x
        vv = v.T @ v
        mu = (vv[0][0] / (len(v) - len(x))) ** 0.5
        q = np.linalg.inv(a.T @ a)
        diagonal_q = np.diag(q)
        mses = np.sqrt(diagonal_q) * mu
        mses_dict = {"mu": float(mu),
                     "v": v.flatten(),
                     "mse_abx": float(mses[0]),
                     "mse_aby": float(mses[1]),
                     "mse_abz": float(mses[2]),
                     "mse_asx": float(mses[3]),
                     "mse_asy": float(mses[4]),
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

