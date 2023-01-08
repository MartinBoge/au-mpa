import matplotlib.pyplot as plt
import pyomo.environ as pyomo

from mpa.utilities.file_utils import read_json
from mpa.utilities.support_functions import create_subsets


def read_data(path: str) -> dict:

    data = read_json(path)

    data["all_subsets"] = create_subsets(data["n"])

    return data


def build_model(data: dict) -> pyomo.ConcreteModel():

    # Instantiate model
    model = pyomo.ConcreteModel()

    # Add data
    model.nodes = range(0, data["n"] + 1)
    model.dist = data["dist"]

    # Define variables
    model.x = pyomo.Var(model.nodes, model.nodes, within=pyomo.Binary)
    for i in model.nodes:
        model.x[i, i].fix(0)

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
        model.sum_to_one.add(expr=sum(model.x[i, j] for i in model.nodes) == 1)
    # Out of node i
    for i in model.nodes:
        model.sum_to_one.add(
            expr=sum(model.x[i, j] for j in model.nodes if i != j) == 1
        )

    # Constraint: Add all the sub-tour elimination constraints
    model.SECs = pyomo.ConstraintList()
    for set in data["all_subsets"]:
        model.SECs.add(
            expr=sum(model.x[i, j] for i in set for j in set if i != j) <= len(set) - 1
        )

    return model


def solve_model(model: pyomo.ConcreteModel()):

    solver = pyomo.SolverFactory("gurobi")

    solver.solve(model, tee=True)


def display_solution(model: pyomo.ConcreteModel(), data: dict):

    optimal_cost = round(pyomo.value(model.obj), 4)

    print(f"Optimal objection function value = {optimal_cost:,}")

    print("Optimal tour is")
    curNode = 0
    print(curNode, "->", end="")
    KeepOn = True
    counter = 0

    # Flag for testing if coordinates are present in the data
    coordinatesPresent = "x_cord" in data and "y_cord" in data
    if coordinatesPresent:
        displayX = [data["x_cord"][0]]
        displayY = [data["y_cord"][0]]
        labels = [0]

    # Find the route from the x[i,j] values
    while KeepOn:
        counter = counter + 1
        # Find next on route
        for i in model.nodes:
            if i != curNode and pyomo.value(model.x[curNode, i]) == 1:
                if coordinatesPresent:
                    displayX.append(data["x_cord"][i])
                    displayY.append(data["y_cord"][i])
                if i > 0:
                    print(i, "->", end="")
                    if coordinatesPresent:
                        labels.append(i)
                else:
                    print(i, end="")
                tmpCurNode = i
        curNode = tmpCurNode
        if curNode < 1:
            break
    print("")

    # Start plotting the solution to a coordinate system
    if coordinatesPresent:
        plt.plot(displayX, displayY, "-o")
        for i, label in enumerate(labels):
            plt.annotate(label, (displayX[i], displayY[i]))
        plt.show()


def display_solution_simple(model: pyomo.ConcreteModel()):

    currentNode = 0

    # Find first on tour:
    for j in model.nodes:
        if pyomo.value(model.x[currentNode, j]) >= 0.9999:
            print("0 ->", j, end="")
            currentNode = j
            break

    # Find the remaining nodes of the tour
    while currentNode != 0:
        # Find the next node
        for j in model.nodes:
            if pyomo.value(model.x[currentNode, j]) >= 0.9999:
                print("->", j, end="")
                currentNode = j
                break

    print("")


def main():
    data = read_data("src/mpa/ruteplanlægning/7_2_0_TSP_DFJ_data.json")
    model = build_model(data)
    solve_model(model)
    # display_solution(model, data)
    display_solution_simple(model)


if __name__ == "__main__":
    main()
