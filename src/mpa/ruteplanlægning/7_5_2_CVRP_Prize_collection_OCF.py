import matplotlib.pyplot as plt
import pyomo.environ as pyomo

from mpa.utilities.file_utils import read_json


def readData(filename: str) -> dict:
    data = read_json(filename)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Create model
    model = pyomo.ConcreteModel()
    # Copy data to model
    model.numOfNodes = data["n"] + 1
    model.n = range(0, model.numOfNodes)
    model.dist = data["dist"]
    model.customers = range(1, model.numOfNodes)
    model.p = data["prize"]
    # Create Variables
    model.x = pyomo.Var(model.n, model.n, within=pyomo.Binary)
    model.y = pyomo.Var(model.customers, within=pyomo.Binary)
    model.f = pyomo.Var(
        model.n, model.n, within=pyomo.NonNegativeReals, bounds=(0, data["Q"])
    )
    # Define objective function
    model.obj = pyomo.Objective(
        expr=sum(model.p[i] * model.y[i] for i in model.customers)
        - sum(model.x[i, j] * model.dist[i][j] for i in model.n for j in model.n),
        sense=pyomo.maximize,
    )
    # Define model constraints
    model.sumToOne = pyomo.ConstraintList()
    for i in model.customers:
        # Out of node i
        model.sumToOne.add(
            expr=sum(model.x[i, j] for j in model.n if i != j) == model.y[i]
        )
        # Into node i
        model.sumToOne.add(
            expr=sum(model.x[j, i] for j in model.n if i != j) == model.y[i]
        )
    # Add the in- and out-degree constraints for the depot
    model.depotInOut = pyomo.ConstraintList()
    # Leave depot
    model.depotInOut.add(expr=sum(model.x[0, j] for j in model.n) <= data["m"])
    # Return to depot
    model.depotInOut.add(expr=sum(model.x[i, 0] for i in model.n) <= data["m"])
    # Add the generalized variable bounds f[i][j] <= (Q-q[j])x[i][j] and f[i][j] >= min(i,1)x[i][j]
    model.GeneralizedBounds = pyomo.ConstraintList()
    for i in model.n:
        for j in model.n:
            model.GeneralizedBounds.add(
                expr=model.f[i, j] <= (data["Q"] - data["q"][j]) * model.x[i, j]
            )
            model.GeneralizedBounds.add(
                expr=model.f[i, j] >= data["q"][i] * model.x[i, j]
            )
    # Add flow-conservation constraint
    model.flowConservation = pyomo.ConstraintList()
    for i in model.customers:
        model.flowConservation.add(
            expr=sum(model.f[i, j] for j in model.n)
            == sum(model.f[j, i] for j in model.n) + data["q"][i] * model.y[i]
        )
    return model


def solveModel(model: pyomo.ConcreteModel()):
    solver = pyomo.SolverFactory("gurobi")
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel(), data: dict):
    print("Total length of the", data["m"], "tours are", pyomo.value(model.obj))
    # Find a tour for each vehicle
    lastRouteStarter = 0
    # Make flag for checking if coordinates are available
    coordinatesPresent = ("xCoord" in data) and ("yCoord" in data)
    # Create a route for each vehicle
    for vehicle in range(1, data["m"] + 1):
        # Each route starts at the depot
        if coordinatesPresent:
            displayX = [data["xCoord"][0]]
            displayY = [data["yCoord"][0]]
            labels = [0]
        # Find the customer, that starts this route
        currentNode = 0
        for j in model.customers:
            if j > lastRouteStarter and pyomo.value(model.x[0, j]) >= 0.9999:
                currentNode = j
                if coordinatesPresent:
                    displayX.append(data["xCoord"][currentNode])
                    displayY.append(data["yCoord"][currentNode])
                    labels.append(currentNode)
                break
        lastRouteStarter = currentNode
        print("The route for vehicle", vehicle, "is:")
        print("0->", currentNode, end="")
        # Build the route from currentNode back to the depot
        while currentNode != 0:
            for j in model.n:
                if currentNode != j and pyomo.value(model.x[currentNode, j]) >= 0.9999:
                    print("->", j, end="")
                    currentNode = j
                    if coordinatesPresent:
                        displayX.append(data["xCoord"][currentNode])
                        displayY.append(data["yCoord"][currentNode])
                        labels.append(currentNode)
                    break
        print("\n")
        if coordinatesPresent:
            # Start plotting the solution to a coordinate system if coordinates are present
            if coordinatesPresent:
                plt.plot(displayX, displayY, "-o")
                for i, label in enumerate(labels):
                    plt.annotate(label, (displayX[i], displayY[i]))
    plt.show()
    for i in model.customers:
        if pyomo.value(model.y[i]) == 1:
            print("Total prize collected is", (model.p[i]))


def main():
    data = readData("src/mpa/ruteplanlægning/7_5_CVRP_data.json")
    model = buildModel(data)
    solveModel(model)
    displaySolution(model, data)


if __name__ == "__main__":
    main()
