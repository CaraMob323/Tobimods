import json
import yaml

def save_json(path: str, name: str, saved: str):
    with open(path+"\\"+name, "w+") as file:
        json.dump(saved, file, indent=4)

def read_json(path: str):
    with open(path, "r", encoding="utf-8-sig") as file:
        return json.load(file)
    
def read_yaml(path: str):
    with open(path, "r") as file:
        return yaml.load(file, Loader = yaml.SafeLoader)
        