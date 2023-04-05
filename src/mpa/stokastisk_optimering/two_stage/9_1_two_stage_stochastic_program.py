import time

import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyomo
from pyomo.environ import quicksum as qsum

from mpa.utilities.file_utils import read_json


def generate_scenarios(data: dict, numScenarios) -> list:
    # Start by putting the expected values into the list of scenarios
    np.random.seed(1)
    scenarios = [data["demand_exp"]]
    # Generate the required number of additional scenarios
    for i in range(numScenarios):
        scenarios.append(
            list(
                np.random.normal(
                    data["demand_exp"], data["demand_std"], data["numCustomers"]
                )
            )
        )
        # Make sure, all demands are non-negative
        for i in range(len(scenarios[-1])):
            if scenarios[-1][i] < 0:
                scenarios[-1][i] = 0
    return scenarios


def read_data(filename: str, numScenarios) -> dict:
    data = read_json(filename)
    data["demand_scenario"] = generate_scenarios(data, numScenarios)
    return data


def build_model(data: dict) -> pyomo.ConcreteModel():
    # Create the model object
    model = pyomo.ConcreteModel()
    # Create ranges
    model.facilities = range(data["numFacilities"])
    model.customers = range(data["numCustomers"])
    model.scenarios = range(len(data["demand_scenario"]))
    model.demands = data["demand_scenario"]
    # Create variables
    model.y = pyomo.Var(model.facilities, within=pyomo.Binary)
    model.x = pyomo.Var(
        model.facilities, model.customers, model.scenarios, within=pyomo.Binary
    )
    # Probability for the scenarios
    prob = 1 / len(data["demand_scenario"])
    # Create the objective function
    model.obj = pyomo.Objective(
        expr=qsum(data["f"][i] * model.y[i] for i in model.facilities)
        + prob
        * qsum(
            data["c"][i][j] * model.demands[k][j] * model.x[i, j, k]
            for i in model.facilities
            for j in model.customers
            for k in model.scenarios
        )
    )
    # Create "sum to one" constraints for all customers and all scenarios
    model.sumToOne = pyomo.ConstraintList()
    for k in model.scenarios:
        for j in model.customers:
            model.sumToOne.add(
                expr=qsum(model.x[i, j, k] for i in model.facilities) == 1
            )
    # Create capacity constraints
    model.capacities = pyomo.ConstraintList()
    for k in model.scenarios:
        for i in model.facilities:
            model.capacities.add(
                expr=qsum(
                    model.demands[k][j] * model.x[i, j, k] for j in model.customers
                )
                <= data["cap"][i] * model.y[i]
            )
    return model


def solve_model(model: pyomo.ConcreteModel()) -> float:
    solver = pyomo.SolverFactory("gurobi")
    solver.options["MIPGap"] = 0.001
    solver.solve(model, tee=False)
    return pyomo.value(model.obj)


def main(filename: str, numScenarios: int):
    objValues = []
    compTimes = []
    scenarios = []
    for sc in range(0, numScenarios + 1, 5):
        print(f"Number of scenarios in the current problem : {sc+1}")
        data = read_data(filename, sc)
        model = build_model(data)
        start = time.time()
        objValues.append(solve_model(model))
        compTimes.append(time.time() - start)
        scenarios.append(sc)
    plt.plot(scenarios, objValues, "o-r")
    plt.ylabel("Objective function values")
    plt.xlabel("Number of scenarios")
    plt.ylim(1000, 1350)
    plt.savefig(
        "src/mpa/stokastisk_optimering/two_stage/obj_values_500.eps",
        bbox_inches="tight",
    )
    plt.clf()

    differences = [
        abs(objValues[i] - objValues[i + 1]) for i in range(len(objValues) - 1)
    ]
    plt.plot(scenarios[1:], differences, "o-r")
    plt.ylabel("Differences in objective function values")
    plt.xlabel("Number of scenarios")
    plt.savefig(
        "src/mpa/stokastisk_optimering/two_stage/obj_diff_500.eps", bbox_inches="tight"
    )
    plt.clf()

    plt.plot(scenarios, compTimes, "o-r")
    plt.ylabel("Computation times in seconds")
    plt.xlabel("Number of scenarios")
    plt.savefig(
        "src/mpa/stokastisk_optimering/two_stage/time_500.eps", bbox_inches="tight"
    )


if __name__ == "__main__":
    main("src/mpa/stokastisk_optimering/9_1_data.json", 50)
