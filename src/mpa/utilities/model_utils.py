import pyomo.environ as pyomo


def solve_model(
    model: pyomo.ConcreteModel(),
    solver: str = "gurobi",
    timelimit: float = None,
    MIPgap: float = None,
):
    """
    Solve a Pyomo ConcreteModel using the specified solver.

    Parameters:
    model (pyomo.environ.ConcreteModel): The Pyomo ConcreteModel to solve.
    solver (str, optional): The name of the solver to use. Default is "gurobi".
    timelimit (float, optional): The time limit for the solver to run, in seconds. Default is None.
    MIPgap (float, optional): The MIP gap tolerance for the solver. Default is None.

    Returns:
    pyomo.opt.base.SolverResults: The solver results.
    """
    solver = pyomo.SolverFactory(solver)

    if timelimit:
        solver.options["timelimit"] = timelimit  # seconds

    if MIPgap:
        solver.options["MIPgap"] = MIPgap  # float percentage

    results = solver.solve(model, tee=True)

    return results
