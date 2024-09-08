import json

def read_json(data_path: str) -> dict:

    with open(data_path, "r") as f:
        data = json.load(f)
        f.close()
    
    return data