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
    model.l = range(0, k)

    # Define variables
    model.x = pyomo.Var(model.i, model.l, within=pyomo.Binary)
    model.D = pyomo.Var(model.l, within=pyomo.NonNegativeReals)
    model.Dmax = pyomo.Var(within=pyomo.NonNegativeReals)

    # Define objective function
    model.obj = pyomo.Objective(
        expr=model.Dmax,
        sense=pyomo.minimize,
    )

    # Constraint: d^max >= D_l
    model.DmaxDefinition = pyomo.ConstraintList()
    for l in model.l:
        model.DmaxDefinition.add(expr=model.Dmax >= model.D[l])

    # Constraint: upper boundary for diameter in cluster l
    model.Dbound = pyomo.ConstraintList()
    for l in model.l:
        for i in model.i:
            for j in model.i:
                if i != j:
                    model.Dbound.add(
                        expr=model.D[l]
                        >= model.dist[i][j] * (model.x[i, l] + model.x[j, l] - 1)
                    )

    # Constraint: non-negative Dbound
    model.DboundNonNeg = pyomo.ConstraintList()
    for l in model.l:
        model.DboundNonNeg.add(expr=model.D[l] >= 0)

    # Constraint: all dataobjects are assign to one cluster:
    model.allAssigned = pyomo.ConstraintList()
    for i in model.i:
        model.allAssigned.add(expr=sum(model.x[i, l] for l in model.l) == 1)

    return model


def solve_model(model: pyomo.ConcreteModel()):

    solver = pyomo.SolverFactory("gurobi")

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel()):

    print("Optimal objection function value =", pyomo.value(model.obj))

    for k in range(0, model.k):
        print("Cluster " + str(k + 1) + " contains: ")
        for n in range(0, model.n):
            if model.x[n, k].value == 1:
                print("    " + model.states[n])

    # Further visualization tool: https://www.mapchart.net/usa.html


def main():
    data = read_data("src/mpa/aflevering_1/USArrests.json")
    model = build_model(data, k=5)
    solve_model(model)
    display_solution(model)


if __name__ == "__main__":
    main()
