import pyomo.environ as pyomo

from mpa.utilities.file_utils import read_json


def read_data(path: str) -> dict:

    data = read_json(path)

    ...

    return data


def build_model(data: dict) -> pyomo.ConcreteModel():

    # Instantiate model
    model = pyomo.ConcreteModel()

    # Add data
    ...

    # Define variables
    ...

    # Define objective function
    model.obj = pyomo.Objective(expr=..., sense=...)

    # Add constraints
    ...

    return model


def solve_model(model: pyomo.ConcreteModel()):

    solver = pyomo.SolverFactory("gurobi")

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel()):

    print("Optimal objection function value =", pyomo.value(model.obj))

    ...


def main():
    data = read_data("path_to_data")
    model = build_model(data)
    solve_model(model)
    display_solution(model)


if __name__ == "__main__":
    main()
