import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

from mpa.utilities.file_utils import read_json


def main():
    k = 3

    # Read data
    data = read_json(path="src/mpa/clustering/data_clustering.json")

    x_coordinates = data["x"]
    y_coordinates = data["y"]

    # Make a list of dataobjects (2-dimensional)
    points = list(zip(x_coordinates, y_coordinates))

    # Create a k-means object with k clusters
    kmeans = KMeans(n_clusters=k)

    # Run the k-means algorithm on the data
    kmeans.fit(points)

    # Plot the data en a scatter plot
    plt.scatter(x_coordinates, y_coordinates, c=kmeans.labels_)
    plt.show()


if __name__ == "__main__":
    main()
