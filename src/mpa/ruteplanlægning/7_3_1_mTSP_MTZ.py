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

    model.m = data["m"]
    model.S = data["S"]

    # Define variables
    model.x = pyomo.Var(model.nodes, model.nodes, within=pyomo.Binary)
    for i in model.nodes:
        model.x[i, i].fix(0)

    model.u = pyomo.Var(
        model.customers, within=pyomo.NonNegativeReals, bounds=(1, model.S)
    )

    # Define objective function
    model.obj = pyomo.Objective(
        expr=sum(
            sum(model.dist[i][j] * model.x[i, j] for j in model.nodes if i != j)
            for i in model.nodes
        ),
        sense=pyomo.minimize,
    )

    # Constraint: in and out of verticies
    model.sum_to_one = pyomo.ConstraintList()
    # In to node j
    for j in model.customers:
        model.sum_to_one.add(
            expr=sum(model.x[i, j] for i in model.nodes if i != j) == 1
        )
    # Out of node i
    for i in model.customers:
        model.sum_to_one.add(
            expr=sum(model.x[i, j] for j in model.nodes if i != j) == 1
        )

    # Constraints: m in and m out of storage
    model.depot_out = pyomo.Constraint(
        expr=sum(model.x[0, j] for j in model.nodes) == model.m
    )
    model.depot_in = pyomo.Constraint(
        expr=sum(model.x[i, 0] for i in model.nodes) == model.m
    )

    # Constraint: each vehicle/salesperson can only service S customers:
    model.service_level = pyomo.ConstraintList()
    for i in model.customers:
        model.service_level.add(expr=1 <= model.u[i])
        model.service_level.add(expr=model.u[i] <= model.S)

    # Constraint: trefold inequality
    model.trefold_ineq = pyomo.ConstraintList()
    for i in model.customers:
        for j in model.customers:
            model.trefold_ineq.add(
                expr=model.u[i]
                - model.u[j]
                + model.S * model.x[i, j]
                + (model.S - 2) * model.x[j, i]
                <= model.S - 1
            )

    return model


def solve_model(model: pyomo.ConcreteModel()):
    solver = pyomo.SolverFactory("gurobi")

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel(), data: dict):
    # Print total length of tours
    print("Total length of tours:", pyomo.value(model.obj))

    # Find a tour for each vehicle
    last_route_starter = 0
    coordinates_present = "x_coord" in data and "y_coord" in data
    for vehicle in range(1, model.m + 1):
        if coordinates_present:
            display_x = [data["x_coord"][0]]
            display_y = [data["y_coord"][0]]
            labels = [0]

        # Find the customer, that starts the next route
        current_node = 0
        for j in model.customers:
            if j > last_route_starter and pyomo.value(model.x[0, j]) >= 0.9999:
                current_node, last_route_starter = j, j

                if coordinates_present:
                    display_x.append(data["x_coord"][current_node])
                    display_y.append(data["y_coord"][current_node])
                    labels.append(current_node)

                break

        print(f"The route for vehicle {vehicle} is:")
        print(f"0 -> {current_node}", end="")

        # Build the route from current node back to the depot
        while current_node != 0:
            for j in model.nodes:
                if (
                    current_node != j
                    and pyomo.value(model.x[current_node, j]) >= 0.9999
                ):
                    print(f" -> {j}", end="")
                    current_node = j
                    if coordinates_present:
                        display_x.append(data["x_coord"][current_node])
                        display_y.append(data["y_coord"][current_node])
                        labels.append(current_node)
                    break

        print("\n")
        if coordinates_present:
            # Start plotting the solution to a coordinate system
            if coordinates_present:
                plt.plot(display_x, display_y, "-o")
                for i, label in enumerate(labels):
                    plt.annotate(label, (display_x[i], display_y[i]))
    plt.show()


def display_solution_simple(model: pyomo.ConcreteModel()):
    optimal_cost = round(pyomo.value(model.obj), 4)

    print(f"Optimal objection function value = {optimal_cost:,}")

    last_route_starter = 0

    for vehicle in range(1, model.m + 1):
        print(f"The route for vehicle {vehicle} is:")
        current_node = 0

        # Find the first node on the route
        for j in model.nodes:
            if (
                j > last_route_starter
                and pyomo.value(model.x[current_node, j]) >= 0.9999
            ):
                print(f"0 -> {j}", end="")
                current_node, last_route_starter = j, j
                break

        # Find the remaining nodes of the route
        while current_node != 0:
            # Find the next node
            for j in model.nodes:
                if pyomo.value(model.x[current_node, j]) >= 0.9999:
                    print(f" -> {j}", end="")
                    current_node = j
                    break

        print("\n")

    print("")


def main():
    data = read_data("src/mpa/ruteplanlægning/7_3_small_data.json")
    model = build_model(data)
    solve_model(model)
    # display_solution(model, data)
    display_solution_simple(model)


if __name__ == "__main__":
    main()
