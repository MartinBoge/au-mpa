import matplotlib.pyplot as plt
import pyomo.environ as pyomo

from mpa.utilities.file_utils import read_json


def read_data(path: str) -> dict:

    data = read_json(path)

    return data


def build_model(data: dict) -> pyomo.ConcreteModel():

    # Instantiate model
    model = pyomo.ConcreteModel()

    # Add data
    model.n = data["n"]
    model.customers = range(
        1, model.n + 1
    )  # Implicitly implies that the storage is node 0

    model.nodes = range(0, data["n"] + 1)
    model.dist = data["dist"]

    # Define variables
    model.x = pyomo.Var(model.nodes, model.nodes, within=pyomo.Binary)
    for i in model.nodes:
        model.x[i, i].fix(0)

    model.u = pyomo.Var(
        model.customers, within=pyomo.NonNegativeReals, bounds=(1, model.n)
    )

    # Define objective function
    model.obj = pyomo.Objective(
        expr=sum(
            sum(model.dist[i][j] * model.x[i, j] for j in model.nodes)
            for i in model.nodes
        ),
        sense=pyomo.minimize,
    )

    # Constraint: in and out of verticies
    model.sum_to_one = pyomo.ConstraintList()
    # In to node j
    for j in model.nodes:
        model.sum_to_one.add(
            expr=sum(model.x[i, j] for i in model.nodes if i != j) == 1
        )
    # Out of node i
    for i in model.nodes:
        model.sum_to_one.add(
            expr=sum(model.x[i, j] for j in model.nodes if i != j) == 1
        )

    # Constraints: Add all the sub-tour elimination constraints
    model.mtz_order = pyomo.ConstraintList()
    for i in model.customers:
        model.mtz_order.add(expr=1 <= model.u[i])
        model.mtz_order.add(expr=model.u[i] <= model.n)

    model.mtz_complete = pyomo.ConstraintList()
    for i in model.customers:
        for j in model.customers:
            model.mtz_complete.add(
                expr=model.u[i] - model.u[j] + model.n * model.x[i, j] <= model.n - 1
            )

    return model


def solve_model(model: pyomo.ConcreteModel()):

    solver = pyomo.SolverFactory("gurobi")

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel(), data: dict):

    optimal_cost = round(pyomo.value(model.obj), 4)

    print(f"Optimal objection function value = {optimal_cost:,}")

    print("Optimal tour is")
    current_node = 0
    print(f"{current_node} -> ", end="")
    counter = 0

    # Flag for testing if coordinates are present in the data
    coordinates_present = "x_cord" in data and "y_cord" in data
    if coordinates_present:
        display_x = [data["x_cord"][0]]
        display_y = [data["y_cord"][0]]
        labels = [0]

    # Find the route from the x[i,j] values
    while True:
        counter = counter + 1
        # Find next on route
        for i in model.nodes:
            if i != current_node and pyomo.value(model.x[current_node, i]) == 1:
                if coordinates_present:
                    display_x.append(data["x_cord"][i])
                    display_y.append(data["y_cord"][i])
                if i > 0:
                    print(f"{i} -> ", end="")
                    if coordinates_present:
                        labels.append(i)
                else:
                    print(i, end="")
                tmpcurrent_node = i
        current_node = tmpcurrent_node
        if current_node < 1:
            break
    print("")

    # Start plotting the solution to a coordinate system
    if coordinates_present:
        plt.plot(display_x, display_y, "-o")
        for i, label in enumerate(labels):
            plt.annotate(label, (display_x[i], display_y[i]))
        plt.show()


def display_solution_simple(model: pyomo.ConcreteModel()):

    optimal_cost = round(pyomo.value(model.obj), 4)

    print(f"Optimal objection function value = {optimal_cost:,}")

    current_node = 0

    # Find first on tour:
    for j in model.nodes:
        if pyomo.value(model.x[current_node, j]) >= 0.9999:
            print("0 ->", j, end="")
            current_node = j
            break

    # Find the remaining nodes of the tour
    while current_node != 0:
        # Find the next node
        for j in model.nodes:
            if pyomo.value(model.x[current_node, j]) >= 0.9999:
                print(f" -> {j}", end="")
                current_node = j
                break

    print("")


def main():
    data = read_data("src/mpa/ruteplanlægning/7_2_data.json")
    model = build_model(data)
    solve_model(model)
    # display_solution(model, data)
    display_solution_simple(model)


if __name__ == "__main__":
    main()
