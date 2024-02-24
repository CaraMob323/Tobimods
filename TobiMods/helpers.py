import json
import yaml

def read_json(self, path: str):
        with open(path, "r", encoding="utf-8-sig") as file:
            return json.load(file)
    
def read_yaml(self, path: str):
        with open(path, "r") as file:
            return yaml.load(file, Loader = yaml.SafeLoader)