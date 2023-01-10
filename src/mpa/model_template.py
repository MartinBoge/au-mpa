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
    ...

    # Define variables
    ...

    # Define objective function
    model.obj = pyomo.Objective(expr=..., sense=...)

    # Constraint:
    ...

    return model


def display_solution(model: pyomo.ConcreteModel(), data: dict, r: int = 2):

    ofc = round(pyomo.value(model.obj), r)
    print(f"\nOptimal objection function value = {ofc}")


def main():
    data = read_data("path_to_data")
    model = build_model(data)
    solve_model(model)
    display_solution(model, data)


if __name__ == "__main__":
    main()
