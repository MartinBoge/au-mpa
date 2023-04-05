import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyomo


def read_data() -> dict:
    data = {
        "products": ["Letmaelk", "Skummetmaelk"],
        "periods": [
            "Week1",
            "Week2",
            "Week3",
            "Week4",
            "Week5",
            "Week6",
            "Week7",
            "Week8",
            "Week9",
            "Week10",
        ],
        "demands": [
            [51989, 58678, 69351, 50036, 38533, 67617, 62777, 38909, 41393, 31850],
            [48011, 41623, 30843, 50561, 61924, 32537, 36922, 60629, 58160, 67854],
        ],
        "var_cost": [
            [2.33, 4.12, 4.68, 4.46, 3.78, 3.68, 5.75, 5.23, 2.60, 3.27],
            [5.67, 3.92, 3.18, 3.51, 4.13, 4.19, 2.05, 2.49, 4.93, 4.39],
        ],
        "fixed_cost": [
            [45000, 45000, 45000, 45000, 45000, 45000, 45000, 45000, 45000, 45000],
            [55000, 55000, 55000, 55000, 55000, 55000, 55000, 55000, 55000, 55000],
        ],
        "inv_cost": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.6, 0.6, 0.6, 0.6],
        "max_prod": 125000,
        "max_inv": 100000,
        "batch_size": 100,
    }

    return data


def build_model(data: dict) -> pyomo.ConcreteModel():
    # Instantiate model
    model = pyomo.ConcreteModel()

    # Add data
    model.t_labels = data["periods"]
    model.k_labels = data["products"]

    model.T = len(data["periods"])
    model.K = len(data["products"])

    model.t = range(0, model.T)
    model.k = range(0, model.K)
    model.p = data["var_cost"]
    model.q = data["fixed_cost"]
    model.h = data["inv_cost"]  # Inventory costs are the same across all products
    model.d = data["demands"]

    model.batch_size = data["batch_size"]

    model.bigM = [sum(row) for row in model.d]

    # Define variables
    model.x = pyomo.Var(
        model.k, model.t, within=pyomo.NonNegativeIntegers, bounds=(0, data["max_prod"])
    )
    model.y = pyomo.Var(model.k, model.t, within=pyomo.Binary)
    model.s = pyomo.Var(
        model.k, model.t, within=pyomo.NonNegativeIntegers, bounds=(0, data["max_inv"])
    )

    # Define objective function
    model.obj = pyomo.Objective(
        expr=sum(
            sum(
                (
                    model.p[k][t] * model.batch_size * model.x[k, t]
                    + model.q[k][t] * model.y[k, t]
                    + model.h[t] * model.s[k, t]
                )
                for t in model.t
            )
            for k in model.k
        ),
        sense=pyomo.minimize,
    )

    # Constraint: demand is met and excess production is added to stock
    model.DemandStock = pyomo.ConstraintList()
    for t in model.t:
        for k in model.k:
            if t == 0:
                model.DemandStock.add(
                    expr=model.x[k, t] == model.d[k][t] + model.s[k, t]
                )
            else:
                model.DemandStock.add(
                    expr=model.s[k, t - 1] + model.x[k, t]
                    == model.d[k][t] + model.s[k, t]
                )

    # Constraint: big-m
    model.bigMConstraint = pyomo.ConstraintList()
    for t in model.t:
        for k in model.k:
            model.bigMConstraint.add(
                expr=model.x[k, t] <= model.bigM[k] * model.y[k, t]
            )

    # Constraint: Open and closing inventory is empty
    model.beginningInventory = pyomo.ConstraintList()
    model.endingInventory = pyomo.ConstraintList()
    for k in model.k:
        model.beginningInventory.add(expr=model.s[k, 0] == 0)
        model.endingInventory.add(expr=model.s[k, model.T - 1] == 0)

    return model


def solve_model(model: pyomo.ConcreteModel()):
    solver = pyomo.SolverFactory("gurobi")

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel()):
    optimal_cost = round(pyomo.value(model.obj), 2)

    print(f"Optimal objection function value = {optimal_cost:,}")

    # Label locations for bars
    pos = np.arange(len(model.t_labels))

    number_of_plots = model.K + 1  # One plot for each product k and one aggregate plot
    number_of_columns = 1

    bar_width = 0.4

    # Creating aggregate production plot ##############################################
    plt.subplot(number_of_plots, number_of_columns, 1)

    x_values = [sum(pyomo.value(model.x[k, t]) for k in model.k) for t in model.t]
    d_values = [sum(model.d[k][t] for k in model.k) for t in model.t]
    s_values = [sum(pyomo.value(model.s[k, t]) for k in model.k) for t in model.t]

    plt.plot(pos, x_values, color="darkred", label="Production level")

    plt.bar(
        pos - bar_width / 2,
        height=d_values,
        label="Demand",
        width=bar_width,
        color="blue",
    )

    plt.bar(
        pos + bar_width / 2,
        height=s_values,
        label="Inventory",
        width=bar_width,
        color="grey",
    )

    plt.title("Aggregate production")
    plt.ylabel("Enheder")
    plt.xticks(pos, model.t_labels)
    plt.legend()

    # Creating individual product plots ###############################################
    for k in model.k:
        plt.subplot(
            number_of_plots, number_of_columns, k + 2
        )  # Starting by plotting the second plot (first k == 0)

        x_values = [pyomo.value(model.x[k, t]) for t in model.t]
        d_values = [pyomo.value(model.d[k][t]) for t in model.t]
        s_values = [pyomo.value(model.s[k, t]) for t in model.t]

        plt.plot(x_values, label="Production level", color="darkred")

        plt.bar(
            pos - bar_width / 2,
            height=d_values,
            label="Demand",
            width=bar_width,
            color="blue",
        )

        plt.bar(
            pos + bar_width / 2,
            height=s_values,
            label="Inventory",
            width=bar_width,
            color="grey",
        )

        product_label = model.k_labels[k]
        plt.title(f"{product_label} (k={k})")
        plt.ylabel("Enheder")
        plt.xticks(pos, model.t_labels)
        plt.legend()

    plt.tight_layout()
    plt.show()


def main():
    data = read_data()
    model = build_model(data)
    solve_model(model)
    display_solution(model)


if __name__ == "__main__":
    main()
