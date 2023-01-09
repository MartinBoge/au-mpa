import pyomo.environ as pyomo

from mpa.utilities.model_utils import solve_model


def read_data() -> dict:
    data = {}
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


def display_solution(model: pyomo.ConcreteModel()):
    print("Optimal objection function value =", pyomo.value(model.obj))

    ...


def main():
    data = read_data()
    model = build_model(data)
    solve_model(model)
    display_solution(model)


if __name__ == "__main__":
    main()
