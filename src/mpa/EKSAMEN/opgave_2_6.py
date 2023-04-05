import pyomo.environ as pyomo

from mpa.utilities.file_utils import read_json


def read_data(path: str) -> dict:
    data = read_json(path)
    return data


def build_model(data: dict) -> pyomo.ConcreteModel():
    # Instantiate model
    model = pyomo.ConcreteModel()

    # Add parameters
    model.T = data["nrPeriods"]
    model.p = data["var_cost"]
    model.h = data["inv_cost"]
    model.d = data["demands"]
    model.M = data["max_production"]

    # Define sets
    model.t = range(0, model.T)

    # Define variables
    model.x = pyomo.Var(
        model.t, within=pyomo.NonNegativeReals, bounds=(0, data["max_production"])
    )
    model.y = pyomo.Var(model.t, within=pyomo.Binary)
    model.s = pyomo.Var(model.t, within=pyomo.NonNegativeReals)

    # Define objective function
    model.obj = pyomo.Objective(
        expr=sum((model.p[t] * model.x[t] + model.h[t] * model.s[t]) for t in model.t),
        sense=pyomo.minimize,
    )

    # Constraint: demand is met and excess production is added to stock
    model.DemandStock = pyomo.ConstraintList()
    for t in model.t:
        if t == 0:
            model.DemandStock.add(expr=model.x[t] == model.d[t] + model.s[t])
        else:
            model.DemandStock.add(
                expr=model.s[t - 1] + model.x[t] == model.d[t] + model.s[t]
            )

    # Constraint: big-m
    model.BigM = pyomo.ConstraintList()
    for t in model.t:
        model.BigM.add(expr=model.x[t] <= model.M * model.y[t])

    # Constraint: stock levels
    model.StockLevels = pyomo.ConstraintList()
    for t in model.t:
        if t == 0 or t - 1 == 15:
            model.StockLevels.add(expr=model.s[t] == 20)
        else:
            model.StockLevels.add(expr=model.s[t] >= 20)

    # Constraint: No more than 7 periods
    model.MaxPeriods = pyomo.Constraint(expr=sum(model.y[i] for i in model.t) <= 5)

    return model


def solve_model(
    model: pyomo.ConcreteModel(),
    solver: str = "gurobi",
    timelimit: float = None,
    MIPgap: float = None,
):
    solver = pyomo.SolverFactory(solver)

    if timelimit:
        solver.options["timelimit"] = timelimit  # seconds

    if MIPgap:
        solver.options["MIPgap"] = MIPgap  # float percentage

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel(), data: dict, r: int = 2):
    ofc = round(pyomo.value(model.obj), r)
    print(f"\nOptimal objection function value = {ofc}")

    print(sum(model.y[i].value for i in model.t))


def main():
    data = read_data("src/mpa/EKSAMEN/ordinary2022Data.json")
    model = build_model(data)
    solve_model(model)
    display_solution(model, data)


if __name__ == "__main__":
    main()
