import pyomo.environ as pyomo

from mpa.utilities.file_utils import read_json
from mpa.utilities.support_functions import make_lp_morm_distance_matrix


def read_data(path: str) -> dict:

    data = read_json(path)

    euclidian_dist_matrix = make_lp_morm_distance_matrix(
        data,
        keys=["murder", "assault", "urbanPop", "rape"],
        p=2,
    )

    data["dist"] = euclidian_dist_matrix

    return data


def build_model(data: dict, k: int) -> pyomo.ConcreteModel():

    # Instantiate model
    model = pyomo.ConcreteModel()

    # Add data
    model.k = k
    model.n = len(data["state"])
    model.states = data["state"]
    model.dist = data["dist"]

    model.i = range(0, model.n)
    model.j = range(0, model.n)

    # Define variables
    model.y = pyomo.Var(model.i, within=pyomo.Binary)
    model.x = pyomo.Var(model.i, model.j, within=pyomo.Binary)

    # Define objective function
    model.obj = pyomo.Objective(
        expr=sum(model.dist[i][j] * model.x[i, j] for i in model.i for j in model.j),
        sense=pyomo.minimize,
    )

    # Constraint: each dataobject is assigned to one group
    model.allAssigned = pyomo.ConstraintList()
    for j in model.j:
        model.allAssigned.add(expr=sum(model.x[i, j] for i in model.i) == 1)

    # Constraint: relationship between x_ij and y_i
    model.relationship = pyomo.ConstraintList()
    for i in model.i:
        for j in model.j:
            model.relationship.add(expr=model.x[i, j] <= model.y[i])

    # Constraint: cardinality with total number of groups
    model.cardinality = pyomo.Constraint(
        expr=sum(model.y[i] for i in model.i) == model.k
    )

    return model


def solve_model(model: pyomo.ConcreteModel()):

    solver = pyomo.SolverFactory("gurobi")

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel()):

    print("Optimal objection function value =", pyomo.value(model.obj))

    for n in range(0, model.n):
        if model.y[n].value == 1:
            rep_state = model.states[n]
            group = []
            for g in range(0, model.n):
                if model.x[n, g].value == 1:
                    group.append(model.states[g])
            group = ", ".join(group)
            print(f"{rep_state} represents the states: {group}")

    # Further visualization tool: https://www.mapchart.net/usa.html


def main():
    data = read_data("src/mpa/aflevering_1/USArrests.json")
    model = build_model(data, k=5)
    solve_model(model)
    display_solution(model)


if __name__ == "__main__":
    main()
