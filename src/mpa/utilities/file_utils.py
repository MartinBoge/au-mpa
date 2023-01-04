import json


def write_json(obj: dict, path: str, indent: int = 4) -> None:
    """
    Write the given object as a JSON file at the specified path.

    Parameters:
    obj (dict): The object to write as a JSON file.
    path (str): The path at which to write the JSON file.
    indent (int, optional): The number of spaces to use for indentation. Defaults to 4.

    Returns:
    None
    """
    with open(path, "w") as write_path:
        json.dump(obj=obj, fp=write_path, indent=indent)


def read_json(path: str) -> dict:
    """
    Read a JSON file at the specified path and return it as a dictionary.

    Parameters:
    path (str): The path of the JSON file to read.

    Returns:
    dict: The contents of the JSON file as a dictionary.
    """
    with open(path) as file:
        return json.load(file)
