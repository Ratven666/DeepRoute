import math

from scipy.optimize import minimize

from deep_route.correction_models.CorrectionModelABC import CorrectionModelABC
from deep_route.oil_well.OilWell import OilWell
from deep_route.oil_well.SubSection import SubSection


class BaseMSACorrectionModel(CorrectionModelABC):

    def __init__(self, oil_well: OilWell, theoretical_b_total, los_func_type="lsm", bad_subsection_percent=0.1):
        super().__init__(oil_well)
        self.theoretical_b_total = theoretical_b_total
        self.current_section_idx = None
        self.current_section = None
        self.los_func_type = los_func_type
        self.bad_subsection_percent = bad_subsection_percent

        if self.los_func_type == "lsm":
            self.loss_function = self._lsm_loss_function
        elif self.los_func_type == "min_abs":
            self.loss_function = self._min_abs_loss_function
        self.bad_subsections = [self.get_bad_subsections(section) for section in self.oil_well]

    def calculate_measure_correction(self):
        for idx, section in enumerate(self.oil_well):
            self.current_section = section
            self.current_section_idx = idx
            correction = self._calculate_section_correction()
            for subsection in section:
                subsection.measure.correction["b_z"] -= correction

    def get_bad_subsections(self, section):
        if self.bad_subsection_percent == 0:
            return set()
        bad_subsections = []
        avr_bh, avr_bv = [], []
        for subsection in section:
            b_v, b_h = self._calk_b_vh_i(subsection, 0)
            avr_bh.append(b_h)
            avr_bv.append(b_v)
        avr_bh = sum(avr_bh) / len(section)
        avr_bv = sum(avr_bv) / len(section)
        for subsection in section:
            b_v, b_h = self._calk_b_vh_i(subsection, 0)
            stat = (b_h - avr_bh) ** 2 + (b_v - avr_bv) ** 2
            bad_subsections.append((subsection, stat))
        bad_subsections = sorted(bad_subsections, key=lambda x: x[1])
        bad_subsections = bad_subsections[-int(len(bad_subsections) * self.bad_subsection_percent):]
        for idx, bad_section in enumerate(bad_subsections):
            bad_subsections[idx] = bad_section[0]
        return set(bad_subsections)

    def _callback_log(self, correction):
        """Callback функция, вызываемая на каждой итерации"""
        f_val = self.loss_function(correction)
        print(f"\tИтерация: x={correction}, f(x)={f_val}")

    def _calculate_section_correction(self):
        print(f"Calculating correction for section {self.current_section} by {self.los_func_type}")
        result = minimize(self.loss_function, x0=0, method='Nelder-Mead', callback=self._callback_log)
        print(result)
        return result.x[0]

    def _lsm_loss_function(self, correction):
        b_v_ref, b_h_ref = self._calk_b_vh_ref()
        loss = 0
        for subsection in self.current_section:
            if subsection in self.bad_subsections[self.current_section_idx]:
                continue
            b_v, b_h = self._calk_b_vh_i(subsection, correction)
            loss += (((b_v - b_v_ref) ** 2 + (b_h - b_h_ref) ** 2) / (len(self.current_section) -
                                                                      len(self.bad_subsections[
                                                                              self.current_section_idx])))
        return loss

    def _min_abs_loss_function(self, correction):
        b_v_ref, b_h_ref = self._calk_b_vh_ref()
        loss = 0
        for subsection in self.current_section:
            if subsection in self.bad_subsections[self.current_section_idx]:
                continue
            b_v, b_h = self._calk_b_vh_i(subsection, correction)
            loss += (abs(b_v - b_v_ref) / (len(self.current_section) -
                                           len(self.bad_subsections[self.current_section_idx]))
                     + abs(b_h - b_h_ref) / (len(self.current_section) -
                                             len(self.bad_subsections[self.current_section_idx])))
        return loss

    @staticmethod
    def _calk_b_vh_i(subsection: SubSection, correction):
        b_z_corr = subsection.measure.b_z - correction
        b_x = subsection.measure.b_x
        b_y = subsection.measure.b_y
        g_x = subsection.measure.g_x
        g_y = subsection.measure.g_y
        g_z = subsection.measure.g_z
        g_t = subsection.measure.g_t

        b_v = (b_x * g_x + b_y * g_y + b_z_corr * g_z) / g_t
        b_h = (b_x ** 2 + b_y ** 2 + b_z_corr ** 2 - b_v ** 2) ** 0.5
        return b_v, b_h

    def _calk_b_vh_ref(self):
        b_v_ref = self.theoretical_b_total * math.sin(math.radians(self.oil_well.dip_ref))
        b_h_ref = self.theoretical_b_total * math.cos(math.radians(self.oil_well.dip_ref))
        return b_v_ref, b_h_ref
