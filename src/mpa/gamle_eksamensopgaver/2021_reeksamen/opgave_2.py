import pyomo.environ as pyomo

from mpa.utilities.file_utils import read_json
from mpa.utilities.model_utils import solve_model


def read_data(path: str) -> dict:
    data = read_json(path)
    return data


def build_model(data: dict) -> pyomo.ConcreteModel():

    # Instantiate model
    model = pyomo.ConcreteModel()

    # Add data
    model.k = 5
    model.n = 38
    model.dist = data["dist"]

    # Add relevant ranges
    model.i = range(0, model.n)
    model.j = range(0, model.n)
    model.l = range(0, model.k)

    # Define variables
    model.x = pyomo.Var(model.i, model.l, within=pyomo.Binary)
    model.d = pyomo.Var(model.l, within=pyomo.NonNegativeReals)
    model.d_max = pyomo.Var(within=pyomo.NonNegativeReals)

    # Define objective function
    model.obj = pyomo.Objective(expr=model.d_max, sense=pyomo.minimize)

    # Constraint: d max
    model.DMAX = pyomo.ConstraintList()
    for l in model.l:
        model.DMAX.add(expr=model.d_max >= model.d[l])

    # Constraint: upper bound
    model.UPPERBOUND = pyomo.ConstraintList()
    for l in model.l:
        for i in model.i:
            for j in model.j:
                if i != j:
                    model.UPPERBOUND.add(
                        expr=model.d[l]
                        >= model.dist[i][j] * (model.x[i, l] + model.x[j, l] - 1)
                    )

    # Constraint: one cluster per customer
    model.SINGLEASSIGNMENT = pyomo.ConstraintList()
    for i in model.i:
        model.SINGLEASSIGNMENT.add(expr=sum(model.x[i, l] for l in model.l) == 1)

    return model


def display_solution(model: pyomo.ConcreteModel(), data: dict):

    print("Optimal objection function value =", pyomo.value(model.obj))

    clusters = [[] for cluster in model.l]

    for i in model.i:
        for l in model.l:
            x_value = model.x[i, l].value
            if x_value == 1:
                clusters[l].append(i)

    for cluster_index in range(len(clusters)):
        print(f"In cluster {cluster_index + 1} are the following customers:")
        for customer_index in range(len(clusters[cluster_index])):
            print(f"    {clusters[cluster_index][customer_index] + 1}")

    print("\n")

    # Diameter for each cluster

    for l in model.d:
        print(model.d[l].value)


def main():
    data = read_data("src/mpa/gamle_eksamensopgaver/2021_reeksamen/opgave_2_data.json")
    model = build_model(data)
    solve_model(model)
    display_solution(model, data)


if __name__ == "__main__":
    main()
