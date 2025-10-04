from deep_route.tests.TestABC import TestABC


class GETTest(TestABC):

    def __init__(self, oil_well, theoretical_gravity=1.):
        super().__init__(oil_well)
        self.theoretical_gravity = theoretical_gravity

    def start_section_test(self, section):
        pass