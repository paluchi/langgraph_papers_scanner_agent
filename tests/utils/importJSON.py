import json


def import_json(file_path: str):
    # Open and load the JSON file
    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    # Now `data` is a Python dictionary containing the JSON data
    return data
