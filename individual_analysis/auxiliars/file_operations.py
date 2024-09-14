import json

def read_json(data_path: str) -> dict:

    with open(data_path, "r") as f:
        data = json.load(f)
        f.close()
    
    return data


def write_json(file_path: str, data: dict) -> None:

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
        f.close()
    