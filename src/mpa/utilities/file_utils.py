import json


def write_json(*, obj: dict, path: str, indent: int = 4) -> None:
    with open(path, "w") as write_path:
        json.dump(obj=obj, fp=write_path, indent=indent)


def read_json(*, path: str) -> dict:
    with open(path) as file:
        return json.load(file)
