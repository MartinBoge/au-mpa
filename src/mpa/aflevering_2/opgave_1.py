import pyomo.environ as pyomo

from mpa.utilities.file_utils import read_json
from mpa.utilities.support_functions import extract_key_names


def read_data(path: str) -> dict:

    data = read_json(path)

    print(extract_key_names(data))

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

    # Constraint:
    ...

    return model


def solve_model(model: pyomo.ConcreteModel()):

    solver = pyomo.SolverFactory("gurobi")

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel()):

    print("Optimal objection function value =", pyomo.value(model.obj))

    ...


def main():
    data = read_data("src/mpa/aflevering_2/dev_data.json")
    # model = build_model(data)
    # solve_model(model)
    # display_solution(model)


if __name__ == "__main__":
    main()
