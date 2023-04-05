import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyomo


def read_data() -> dict:
    data = {
        "periods": [
            "week1",
            "week2",
            "week3",
            "week4",
            "week5",
            "week6",
            "week7",
            "week8",
            "week9",
            "week10",
        ],
        "demands": [
            100_000,
            100_301,
            100_194,
            100_597,
            100_457,
            100_154,
            99_699,
            99_538,
            99_553,
            99_704,
        ],
        "var_cost": [4.00, 4.02, 3.93, 3.99, 3.96, 3.94, 3.9, 3.86, 3.76, 3.83],
        "fixed_cost": [
            50_000,
            50_000,
            50_000,
            50_000,
            50_000,
            50_000,
            50_000,
            50_000,
            50_000,
            50_000,
        ],
        "inv_cost": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.6, 0.6, 0.6, 0.6],
        "max_prod": 125_000,
        "max_inv": 100_000,
    }

    return data


def build_model(data: dict) -> pyomo.ConcreteModel():
    # Instantiate model
    model = pyomo.ConcreteModel()

    # Add data
    model.t_labels = data["periods"]

    model.T = len(data["periods"])
    model.t = range(0, model.T)
    model.p = data["var_cost"]
    model.q = data["fixed_cost"]
    model.h = data["inv_cost"]
    model.d = data["demands"]

    model.bigM = sum(model.d)

    # Define variables
    model.x = pyomo.Var(
        model.t, within=pyomo.NonNegativeIntegers, bounds=(0, data["max_prod"])
    )
    model.y = pyomo.Var(model.t, within=pyomo.Binary)
    model.s = pyomo.Var(
        model.t, within=pyomo.NonNegativeIntegers, bounds=(0, data["max_inv"])
    )

    # Define objective function
    model.obj = pyomo.Objective(
        expr=sum(
            (
                model.p[t] * model.x[t]
                + model.q[t] * model.y[t]
                + model.h[t] * model.s[t]
            )
            for t in model.t
        ),
        sense=pyomo.minimize,
    )

    # Constraint: demand is met and excess production is added to stock
    model.DemandStock = pyomo.ConstraintList()
    for t in model.t:
        if t == 0:
            model.DemandStock.add(expr=model.x[t] == model.d[t] + model.s[t])
        else:
            model.DemandStock.add(
                expr=model.s[t - 1] + model.x[t] == model.d[t] + model.s[t]
            )

    # Constraint: big-m
    model.bigMConstraint = pyomo.ConstraintList()
    for t in model.t:
        model.bigMConstraint.add(expr=model.x[t] <= model.bigM * model.y[t])

    # Constraint: Open and closing inventory is empty
    model.beginningInventory = pyomo.Constraint(expr=model.s[0] == 0)
    model.endingInventory = pyomo.Constraint(expr=model.s[model.T - 1] == 0)

    return model


def solve_model(model: pyomo.ConcreteModel()):
    solver = pyomo.SolverFactory("gurobi")

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel()):
    optimal_cost = round(pyomo.value(model.obj), 2)

    print(f"Optimal objection function value = {optimal_cost:,}")

    # Number of periods - used to control placement on the x-axis
    numPeriods = len(model.t_labels)

    # Position of bars on x-axis
    pos = np.arange(numPeriods)

    # Extract the optimal variable values
    s_values = [pyomo.value(model.s[t]) for t in model.t]
    x_values = [pyomo.value(model.x[t]) for t in model.t]

    # Width of the bars
    width = 0.4

    # Add the three plots to the fig-figure
    plt.bar(pos, model.d, width, label="Demands", color="blue")
    plt.bar(pos + width, s_values, width, label="Inventory level", color="grey")
    plt.plot(pos, x_values, color="darkred", label="Production level")

    # Set the ticks on the x-axis
    plt.xticks(pos + width / 2, model.t_labels)

    # Labels on axis
    plt.xlabel("Periods to plan")
    plt.ylabel("Demand")
    plt.title(f"Optimal production plan. Optimal cost is: {(optimal_cost):,}")

    # Show the figure
    plt.show()


def main():
    data = read_data()
    model = build_model(data)
    solve_model(model)
    display_solution(model)


if __name__ == "__main__":
    main()
