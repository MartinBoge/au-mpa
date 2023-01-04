from typing import List

import numpy as np


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
