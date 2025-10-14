import math

from scipy.optimize import minimize

from deep_route.correction_models.CorrectionModelABC import CorrectionModelABC
from deep_route.oil_well.OilWell import OilWell
from deep_route.oil_well.SubSection import SubSection


class BaseMSACorrectionModel(CorrectionModelABC):

    def __init__(self, oil_well: OilWell, theoretical_b_total, los_func_type="lsm"):
        super().__init__(oil_well)
        self.theoretical_b_total = theoretical_b_total
        self.current_section = None
        self.los_func_type = los_func_type
        if self.los_func_type == "lsm":
            self.loss_function = self.lsm_loss_function
        elif self.los_func_type == "min_abs":
            self.loss_function = self.min_abs_loss_function

    def calculate_measure_correction(self):
        for section in self.oil_well:
            self.current_section = section
            correction = self._calculate_section_correction()
            for subsection in section:
                subsection.measure.correction["b_z"] += correction

    def callback_log(self, correction):
        """Callback функция, вызываемая на каждой итерации"""
        f_val = self.loss_function(correction)
        print(f"\tИтерация: x={correction}, f(x)={f_val}")

    def _calculate_section_correction(self):
        print(f"Calculating correction for section {self.current_section} by {self.los_func_type}")
        result = minimize(self.loss_function, x0=0, method='Nelder-Mead', callback=self.callback_log)
        print(result)
        return result.x[0]

    def lsm_loss_function(self, correction):
        b_v_ref, b_h_ref = self._calk_b_vh_ref()
        loss = 0
        for subsection in self.current_section:
            b_v, b_h = self.calk_b_vh_i(subsection, correction)
            loss += ((b_v - b_v_ref)**2 + (b_h - b_h_ref)**2) / len(self.current_section)
        return loss

    def min_abs_loss_function(self, correction):
        b_v_ref, b_h_ref = self._calk_b_vh_ref()
        loss = 0
        for subsection in self.current_section:
            b_v, b_h = self.calk_b_vh_i(subsection, correction)
            loss += abs(b_v - b_v_ref) / len(self.current_section) + abs(b_h - b_h_ref) / len(self.current_section)
        return loss


    @staticmethod
    def calk_b_vh_i(subsection: SubSection, correction):
        b_z_corr = subsection.measure.b_z - correction
        b_x = subsection.measure.b_x
        b_y = subsection.measure.b_y
        g_x = subsection.measure.g_x
        g_y = subsection.measure.g_y
        g_z = subsection.measure.g_z
        g_t = subsection.measure.g_t

        b_v = (b_x*g_x + b_y*g_y + b_z_corr*g_z) / g_t
        b_h = (b_x**2 + b_y**2 + b_z_corr**2 - b_v**2) ** 0.5
        return b_v, b_h

    def _calk_b_vh_ref(self):
        b_v_ref = self.theoretical_b_total * math.sin(math.radians(self.oil_well.dip_ref))
        b_h_ref = self.theoretical_b_total * math.cos(math.radians(self.oil_well.dip_ref))
        return b_v_ref, b_h_ref
