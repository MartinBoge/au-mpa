import pyomo.environ as pyomo


def read_data() -> dict:

    data = {
        "I": [1, 2, 3],
        "J": [1, 2, 3, 4, 5, 6],
        "c": [
            [500, 500, 500, 1000, 1000, 1000],
            [1000, 1000, 150, 150, 1000, 1000],
            [1000, 1000, 1000, 900, 900, 100],
        ],
        "p": 2,
    }

    return data


def build_model(data: dict) -> pyomo.ConcreteModel():

    # Instantiate model
    model = pyomo.ConcreteModel()

    # Add data
    model.i_labels = data["I"]
    model.i = range(0, len(data["I"]))
    model.j = range(0, len(data["J"]))
    model.c = data["c"]
    model.p = data["p"]

    # Define variables
    model.y = pyomo.Var(model.i, within=pyomo.Binary)
    model.x = pyomo.Var(model.i, model.j, within=pyomo.Binary)
    model.rhoMax = pyomo.Var(within=pyomo.NonNegativeReals)

    # Define objective function
    model.obj = pyomo.Objective(
        expr=model.rhoMax,
        sense=pyomo.minimize,
    )

    # Constraint: all customers served
    model.allServed = pyomo.ConstraintList()
    for j in model.j:
        model.allServed.add(expr=sum(model.x[i, j] for i in model.i) == 1)

    # Constraint: point j can be serviced from all open facilities
    model.servedBy = pyomo.ConstraintList()
    for i in model.i:
        for j in model.j:
            model.servedBy.add(expr=model.x[i, j] <= model.y[i])

    # Constrain: rho max definition
    model.rhoMaxDefinition = pyomo.ConstraintList()
    for j in model.j:
        model.rhoMaxDefinition.add(
            expr=sum(model.c[i][j] * model.x[i, j] for i in model.i) <= model.rhoMax
        )

    # Constraint: p facilities are chosen
    model.pFacilities = pyomo.Constraint(
        expr=sum(model.y[i] for i in model.i) == model.p
    )

    return model


def solve_model(model: pyomo.ConcreteModel()):

    solver = pyomo.SolverFactory("gurobi")

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel()):

    print(" ")

    print("Optimal objection function value =", pyomo.value(model.obj))

    facilities = {}
    for i in model.y:
        if model.y[i].value == 1:
            facilities[model.i_labels[i]] = 1
        else:
            facilities[model.i_labels[i]] = 0

    print(" ")

    print("There are placed facilities at: ")
    for facility, y in facilities.items():
        if y == 1:
            print(f"    {facility}")

    print(" ")

    print("The are NOT placed a facility at:")
    for facility, y in facilities.items():
        if y == 0:
            print(f"    {facility}")


def main():
    data = read_data()
    model = build_model(data)
    solve_model(model)
    display_solution(model)


if __name__ == "__main__":
    main()
