import unittest

import pyomo.environ as pyomo  # noqa
from pyomo.opt import SolverStatus  # noqa

from mpa.utilities.model_utils import solve_model  # noqa


# To be implemented. Requires solver to be installed to test vm
class TestModelUtils(unittest.TestCase):
    def test_solve_model_with_gurobi(self):
        self.assertEqual(True, True)

    def test_solve_model_with_timelimit(self):
        self.assertEqual(True, True)

    def test_solve_model_with_mipgap(self):
        self.assertEqual(True, True)


if __name__ == "__main__":
    unittest.main()
