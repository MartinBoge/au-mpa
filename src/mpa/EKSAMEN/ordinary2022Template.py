import pyomo.environ as pyomo
import json as js


def readData(filename: str) -> dict:
    """! This function reads data specified in a json-formatted file to a python dictionary.
        After this, it prints all keys in the dictionary to the prompt for inspection.
        Finally, it returns the dictionary, so it may be used in subsequent procedures.
    """
    with open(filename) as d:
        data = js.load(d)
    print('All keys of the data dictionary are', data.keys())
    return data


def buildModel(data:dict) -> pyomo.ConcreteModel():
    # Implement your own buildModel-function
    model = pyomo.ConcreteModel()
    # Code goes here
    return model


def solveModel(model: pyomo.ConcreteModel()):
    # Implement your own solveModel-function
    pass


def displaySolution(model: pyomo.ConcreteModel()):
    # Implement your own solveModel-function
    pass


def main(filename: str):
    data = readData(filename)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    main('ordinary2022Data.json')