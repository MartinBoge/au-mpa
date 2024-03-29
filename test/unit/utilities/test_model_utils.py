import unittest

import pyomo.environ as pyomo
import pytest
from pyomo.opt import SolverStatus

from mpa.utilities.model_utils import solve_model


@pytest.mark.skip(
    reason="To be implemented. Requires solver to be installed to test vm"
)
class TestModelUtils(unittest.TestCase):
    def test_solve_model_with_gurobi(self):
        # Create a simple Pyomo ConcreteModel
        model = pyomo.ConcreteModel()
        model.x = pyomo.Var()
        model.obj = pyomo.Objective(expr=model.x)
        model.constraint = pyomo.Constraint(expr=model.x >= 1)

        # Solve the model using the Gurobi solver
        results = solve_model(model, solver="gurobi")

        # Check that the solver status is ok
        self.assertEqual(results.solver.status, SolverStatus.ok)

        # Check that the optimal solution was found
        self.assertEqual(
            results.solver.termination_condition, pyomo.TerminationCondition.optimal
        )

    def test_solve_model_with_timelimit(self):
        ...

    def test_solve_model_with_mipgap(self):
        ...


if __name__ == "__main__":
    unittest.main()
