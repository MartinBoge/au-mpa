import matplotlib.pyplot as plt
import numpy as np
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
    model.I = range(0, len(data["I"]))
    model.J = range(0, len(data["J"]))
    model.f = data["f"]
    model.a = data["a"]

    # Define variables
    model.y = pyomo.Var(model.I, within=pyomo.Binary)

    # Define objective function
    model.obj = pyomo.Objective(
        expr=sum(model.f[i] * model.y[i] for i in model.I), sense=pyomo.minimize
    )

    # Constraint: less than 3 km to each center form each village
    model.DISTANCE = pyomo.ConstraintList()
    for j in model.J:
        model.DISTANCE.add(expr=sum(model.a[i][j] * model.y[i] for i in model.I) >= 1)

    return model


def display_solution(model: pyomo.ConcreteModel(), r: int = 2):

    ofc = round(pyomo.value(model.obj), r)
    print(f"\nOptimal objection function value = {ofc}")


def display_solution_graf(model: pyomo.ConcreteModel(), data: dict):

    placerede_testcentre = [data["I"][i] for i in model.I if model.y[i].value == 1]

    print(
        f"\nDer er placeret {len(placerede_testcentre)} testcentre i følgende koordinater:"
    )
    for testcenter in placerede_testcentre:
        print(f"    {testcenter}")

    placerede_testcentre = np.array(placerede_testcentre)
    x_tc, y_tc = placerede_testcentre.T

    landsbyer = data["J"]
    landsbyer = np.array(landsbyer)
    x_lb, y_lb = landsbyer.T

    plt.scatter(x_tc, y_tc, color="red")
    plt.scatter(x_lb, y_lb, color="blue")

    plt.xlabel("x-koordinat")
    plt.ylabel("y-koordinat")

    plt.show()


def main():
    data = read_data(
        "src/mpa/gamle_eksamensopgaver/2021_ordinær/2021_ordinær_data.json"
    )
    model = build_model(data)
    solve_model(model)
    display_solution(model)
    display_solution_graf(model, data)


if __name__ == "__main__":
    main()
