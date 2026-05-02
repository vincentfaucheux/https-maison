
from pathlib import Path
import json


def write_json2file(data):
    # Delete the old file if it exists
    try:
        File = Path("Config.json")
        File.unlink()
    except FileNotFoundError:
        pass

    # Write the new data to Config.json
    with open("Config.json", 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.close()

def read_file2json(data_out):
    try:
        with open("Config.json", "r", encoding="utf-8") as f:
            data_out.clear()
            data_out.update(json.load(f))
        return 0, "OK"
    except FileNotFoundError:
        return -1, "Fichier introuvable"
    except json.JSONDecodeError:
        return -2, "JSON invalide"

def read_string2fulljson(in_string, out_json):
    try:
        out_json.clear()
        out_json.update(json.loads(in_string))
        return 0, "OK"
    except json.JSONDecodeError:
        return -2, "string not a json"

def read_string2partialjson(in_string, out_json):
    try:
        temp_json = json.loads(in_string)
        out_json = deep_merge(out_json, temp_json)
        return 0, "OK"
    except json.JSONDecodeError:
        return -2, "string not a json"

def deep_merge(d1, d2):
    for key, value in d2.items():
        if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
            deep_merge(d1[key], value)
        else:
            d1[key] = value
    return d1

def write_json2string(data):
    try:
        return 0, json.dumps(data, indent=4)
    except (TypeError, ValueError) as e:
        return -1, f"Data not serializable: {e}"

