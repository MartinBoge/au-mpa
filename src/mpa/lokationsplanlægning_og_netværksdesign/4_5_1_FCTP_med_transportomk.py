import pyomo.environ as pyomo


def read_data() -> dict:

    data = {
        "I": ["Fabrik 1", "Fabrik 2", "Fabrik 3", "Fabrik 4", "Fabrik 5"],
        "J": ["Kunde 1", "Kunde 2", "Kunde 3"],
        "s": [100, 100, 200, 150, 75],
        "d": [150, 125, 100],
        "c": [
            [10, 10, 15],
            [15, 20, 10],
            [20, 15, 15],
            [10, 15, 10],
            [20, 5, 5],
        ],
        "f": [
            [10, 10, 15],
            [5, 25, 10],
            [10, 20, 5],
            [15, 15, 10],
            [20, 20, 20],
        ],
    }

    return data


def build_model(data: dict) -> pyomo.ConcreteModel():

    # Instantiate model
    model = pyomo.ConcreteModel()

    # Add data
    model.i_labels = data["I"]
    model.i = range(0, len(data["I"]))
    model.j_labels = data["J"]
    model.j = range(0, len(data["J"]))
    model.s = data["s"]
    model.d = data["d"]
    model.c = data["c"]
    model.f = data["f"]

    model.m = 1_000

    # Define variables
    model.g = pyomo.Var(model.i, model.j, within=pyomo.NonNegativeReals)
    model.y = pyomo.Var(model.i, model.j, within=pyomo.Binary)

    # Define objective function
    model.obj = pyomo.Objective(
        expr=sum(sum(model.c[i][j] * model.g[i, j] for j in model.j) for i in model.i)
        + sum(sum(model.f[i][j] * model.y[i, j] for j in model.j) for i in model.i),
        sense=pyomo.minimize,
    )

    # Constraint: each customer receives their demand
    model.demandMet = pyomo.ConstraintList()
    for j in model.j:
        model.demandMet.add(expr=sum(model.g[i, j] for i in model.i) >= model.d[j])

    # Constraint: each factory stay within their capacity
    model.factoryCapacity = pyomo.ConstraintList()
    for i in model.i:
        model.factoryCapacity.add(
            expr=sum(model.g[i, j] for j in model.j) <= model.s[i]
        )

    # Constraint: big-m
    model.bigM = pyomo.ConstraintList()
    for i in model.i:
        for j in model.j:
            model.bigM.add(expr=model.g[i, j] <= model.m * model.y[i, j])

    # Constraint: non-negativity
    model.nonNegativity = pyomo.ConstraintList()
    for i in model.i:
        for j in model.j:
            model.nonNegativity.add(expr=model.g[i, j] >= 0)

    return model


def solve_model(model: pyomo.ConcreteModel()):

    solver = pyomo.SolverFactory("gurobi")

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel()):

    print("Optimal objection function value =", pyomo.value(model.obj))

    for i in model.i:
        for j in model.j:
            if model.g[i, j].value == 0:
                continue
            else:
                units = model.g[i, j].value
            factory = model.i_labels[i]
            customer = model.j_labels[j]
            print(f"From {factory} {units} units are delivered to {customer}")


def main():
    data = read_data()
    model = build_model(data)
    solve_model(model)
    display_solution(model)


if __name__ == "__main__":
    main()
