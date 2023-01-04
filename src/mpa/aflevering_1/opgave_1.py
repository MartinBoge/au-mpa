from mpa.utilities.distance_matrix_calc import make_lp_morm_distance_matrix
from mpa.utilities.file_utils import read_json
from mpa.utilities.support_functions import extract_key_names


def main():

    data = read_json(path="src/mpa/aflevering_1/USArrests.json")

    print("Keys in data as read from file: ", extract_key_names(data))

    # Euclidian distance matrix as p=2
    euclidian_dist_matrix = make_lp_morm_distance_matrix(
        data=data,
        keys=["murder", "assault", "urbanPop", "rape"],
        p=2,
    )

    # Manhattan distance matrix as p=1
    manhattan_dist_matrix = make_lp_morm_distance_matrix(
        data=data,
        keys=["murder", "assault", "urbanPop", "rape"],
        p=1,
    )

    data["euclidian_dist_matrix"] = euclidian_dist_matrix
    data["manhattan_dist_matrix"] = manhattan_dist_matrix


if __name__ == "__main__":
    main()
