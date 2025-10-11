import math
from abc import abstractmethod

from deep_route.oil_well.Section import Section
from deep_route.oil_well.SubSection import SubSection
from deep_route.tests.TestABC import TestABC


class MagnetometerTestABC(TestABC):

    @abstractmethod
    def start_section_test(self, section: Section):
        pass

    @staticmethod
    def get_derivatives(sub_section: SubSection):
        measure = sub_section.measure
        a_m = sub_section.magnetic_azimuth
        t_f = sub_section.tool_face
        zenith = sub_section.zenith
        dip_ref = sub_section.dip_ref

        derivative_db_mbx = measure.b_x / measure.b_t
        derivative_db_mby = measure.b_y / measure.b_t
        derivative_db_mbz = measure.b_z / measure.b_t

        derivative_db_msx = (measure.b_x**2) / measure.b_t
        derivative_db_msy = (measure.b_y**2) / measure.b_t
        derivative_db_msz = (measure.b_z**2) / measure.b_t

        derivative_db_mfi = -1
        derivative_dd_mdi = -1
        #############################################################################################
        cz_sam = math.cos(zenith) * math.sin(a_m)
        cz_cam = math.cos(zenith) * math.cos(a_m)
        cdr_bt = math.cos(dip_ref) / measure.b_t
        sdr_bt = math.sin(dip_ref) / measure.b_t

        derivative_dd_mbx = (-cdr_bt * math.sin(zenith) * math.sin(t_f) -
                             sdr_bt * (cz_cam * math.sin(t_f) + math.sin(a_m) * math.cos(t_f)))
        derivative_dd_mby = (-cdr_bt * math.sin(zenith) * math.cos(t_f) -
                             sdr_bt * (cz_cam * math.cos(t_f) - math.sin(a_m) * math.sin(t_f)))
        derivative_dd_mbz = (cdr_bt * math.cos(zenith) -
                             sdr_bt * math.sin(zenith) * math.cos(a_m))

        derivative_dd_msx = measure.b_x * derivative_dd_mbx
        derivative_dd_msy = measure.b_y * derivative_dd_mby
        derivative_dd_msz = measure.b_z * derivative_dd_mbz

        #############################################################################################

        denominator = math.sqrt(1 - (math.sin(zenith) ** 2) * (math.sin(a_m) ** 2))

        derivative_dbd_mbix = (cz_sam * math.cos(t_f) + math.cos(a_m) * math.sin(t_f)) / denominator
        derivative_dbd_mbiy = (cz_sam * math.sin(t_f) - math.cos(a_m) * math.cos(t_f)) / denominator
        derivative_dbd_msix = measure.b_x * derivative_dbd_mbix
        derivative_dbd_msiy = measure.b_y * derivative_dbd_mbiy

        # derivative_dbd_msix = measure.b_x * (cz_sam * math.cos(t_f) + math.cos(a_m) * math.sin(t_f)) / denominator
        # derivative_dbd_msiy = measure.b_y * (cz_sam * math.sin(t_f) - math.cos(a_m) * math.cos(t_f)) / denominator

        derivative_dbd_mfi = (math.cos(dip_ref) * math.cos(zenith) -
                          math.sin(dip_ref) * math.sin(zenith) * math.cos(a_m)) / denominator
        derivative_dbd_mdi = measure.b_t * (math.cos(dip_ref) * math.sin(zenith) * math.cos(a_m) +
                                        math.sin(dip_ref) * math.cos(zenith)) / denominator

        return {"db_mbx": derivative_db_mbx,
                "db_mby": derivative_db_mby,
                "db_mbz": derivative_db_mbz,
                "db_msx": derivative_db_msx,
                "db_msy": derivative_db_msy,
                "db_msz": derivative_db_msz,

                "db_mfi": derivative_db_mfi,
                "dd_mdi": derivative_dd_mdi,

                "dd_mbx": derivative_dd_mbx,
                "dd_mby": derivative_dd_mby,
                "dd_mbz": derivative_dd_mbz,
                "dd_msx": derivative_dd_msx,
                "dd_msy": derivative_dd_msy,
                "dd_msz": derivative_dd_msz,

                "dbd_mbix": derivative_dbd_mbix,
                "dbd_mbiy": derivative_dbd_mbiy,
                "dbd_msix": derivative_dbd_msix,
                "dbd_msiy": derivative_dbd_msiy,
                "dbd_mfi": derivative_dbd_mfi,
                "dbd_mdi": derivative_dbd_mdi,
                }
