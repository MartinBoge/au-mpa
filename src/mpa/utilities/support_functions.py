from typing import List

import numpy as np


def extract_key_names(dictionary: dict) -> list:
    """
    Extract the keys from a dictionary as a list.

    Parameters:
    dictionary (dict): The dictionary from which to extract the keys.

    Returns:
    list: A list of keys extracted from the dictionary.
    """
    return list(dictionary.keys())


def make_lp_morm_distance_matrix(data: dict, keys: List[str], p: int) -> list:
    """
    Compute the Lp-norm distance matrix for the given data.

    Parameters:
    data (dict): A dictionary with keys corresponding to the data points and values corresponding to the data itself.
    keys (List[str]): A list of keys corresponding to the data points to be included in the distance matrix.
    p (int): If 1, then Manhattan (Taxi cap) distance. If 2, then Euclidian distance.

    Returns:
    list: A list representing the distance matrix where the i-th row and j-th column represent the Lp-norm distance between the i-th and j-th data points.
    """

    if p == 1:
        print("Creating Manhattan (Taxi cap) distance matrix")

    if p == 2:
        print("Creating Euclidian distance matrix")

    points = np.column_stack([data[key] for key in keys])
    nrPoints = len(data[keys[0]])
    dist = []
    for i in range(0, nrPoints):
        dist.append([])
        for j in range(0, nrPoints):
            dist[i].append(np.linalg.norm(points[i] - points[j], p))
    return dist


# From lecturer #######################################################################
def makeLpNormDistanceMatrix(data: dict, p: int) -> list:
    points = np.column_stack(
        (data["Murder"], data["Assault"], data["UrbanPop"], data["Rape"])
    )
    nrPoints = len(data["Murder"])
    dist = []
    for i in range(0, nrPoints):
        dist.append([])
        for j in range(0, nrPoints):
            dist[i].append(np.linalg.norm(points[i] - points[j], p))
    return dist


def create_subsets(n: int) -> list:
    """
    Create a list of all subsets given a number of customers

    Parameters:
    n (int): The number of customers. (The storage is not counted as it is considered to be 0)

    Returns:
    list: A list of all subsets.
    """
    s = list(range(1, n + 1))
    all_subsets = []
    for i in range(1, 2**n + 1):
        nextList = [s[j] for j in range(n) if (i & (1 << j))]
        nextListLength = len(nextList)
        if 2 <= nextListLength <= n - 1:
            all_subsets.append(nextList)
    return all_subsets


# From lecturer #######################################################################
def powerset(s: list) -> list:
    x = len(s)
    allSubSets = []
    for i in range(1 << x):
        nextList = [s[j] for j in range(x) if (i & (1 << j))]
        nextListLength = len(nextList)
        if 2 <= nextListLength <= x - 1:
            allSubSets.append(nextList)
    return allSubSets


print(create_subsets(4))
