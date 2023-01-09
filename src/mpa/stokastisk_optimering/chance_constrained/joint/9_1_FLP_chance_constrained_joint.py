import time

import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyomo
from pyomo.environ import quicksum as qsum

from mpa.utilities.file_utils import read_json


def generate_scenarios(data: dict, numScenarios) -> list:
    # Start by putting the expected values into the list of scenarios
    scenarios = [data["demand_exp"]]
    np.random.seed(1)
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


def build_model(data: dict, alpha: float) -> pyomo.ConcreteModel():
    # Create the model object
    model = pyomo.ConcreteModel()
    # Create ranges and copy data
    model.facilities = range(data["numFacilities"])
    model.customers = range(data["numCustomers"])
    model.scenarios = range(len(data["demand_scenario"]))
    model.demands = data["demand_scenario"]
    bigM = [
        [sum(data["demand_scenario"][k]) - data["cap"][i] for k in model.scenarios]
        for i in model.facilities
    ]
    # Create variables
    model.y = pyomo.Var(model.facilities, within=pyomo.Binary)
    model.x = pyomo.Var(
        model.facilities, model.customers, model.scenarios, within=pyomo.Binary
    )
    model.z = pyomo.Var(model.scenarios, within=pyomo.Binary)
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
                <= data["cap"][i] * model.y[i] + bigM[i][k] * model.z[k]
            )
    # make sure, that y[i] = 0 => x[i,j,k] = 0 for all i, j and k
    model.forceOpen = pyomo.ConstraintList()
    for k in model.scenarios:
        for i in model.facilities:
            model.forceOpen.add(
                expr=qsum(model.x[i, j, k] for j in model.customers)
                <= data["numCustomers"] * model.y[i]
            )
    # Create upper bound on number of z-variables
    model.chanceCst = pyomo.Constraint(
        expr=qsum(prob * model.z[k] for k in model.scenarios) <= 1 - alpha
    )

    return model


def solve_model(model: pyomo.ConcreteModel()) -> float:
    solver = pyomo.SolverFactory("gurobi")
    solver.solve(model, tee=False)
    return pyomo.value(model.obj)


def main(filename: str, numScenarios: int):
    data = read_data(filename, numScenarios)
    sshs = [0.80 + 0.01 * i for i in range(0, 21)]
    objVals = []
    compTimes = []
    for ssh in sshs:
        print("Probability level is now", ssh, end="\t")
        model = build_model(data, ssh)
        start = time.time()
        objVals.append(solve_model(model))
        compTimes.append(time.time() - start)
        print("objective value: ", objVals[-1], "\tSolution time:", compTimes[-1])
    plt.plot(sshs, objVals, "-o")
    plt.savefig(
        "src/mpa/stokastisk_optimering/chance_constrained/joint/chance_constraints_value_joint.eps",
        bbox_inches="tight",
    )
    plt.clf()
    plt.plot(sshs, compTimes, "-o")
    plt.savefig(
        "src/mpa/stokastisk_optimering/chance_constrained/joint/chance_constraints_time_joint.eps",
        bbox_inches="tight",
    )


if __name__ == "__main__":
    main("src/mpa/stokastisk_optimering/9_1_data.json", 2)
